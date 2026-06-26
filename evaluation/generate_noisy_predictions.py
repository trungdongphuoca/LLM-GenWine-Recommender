import sys, os, json, re, time
import torch
import pandas as pd
from tqdm import tqdm
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

sys.path.insert(0, str(__import__('pathlib').Path(__file__).parents[1]))
import config as cfg

# --- Config Paths ---
NOISY_TEST_PATH = 'data/processed/wine_test_noisy_130k.jsonl'
OUTPUT_CSV = str(cfg.RESULTS / "noisy_constrained_eval_results.csv")

# ─── PROMPT ──────────────────────────────────────────────────────────────────
PROMPT_TEMPLATE = (
    "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
    "You are a Master Sommelier. Analyze the user's request and determine "
    "the ideal structural profile of the wine. Then, output the Semantic ID "
    "of the perfect match in the format [XX-XX-XX-XXX], followed by a brief explanation."
    "<|eot_id|><|start_header_id|>user<|end_header_id|>\n"
    "{instruction}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
)

ID_PAT = r'\d{2}-\d{2}-\d{2}-\d{3}'

def parse_semantic_id(text: str) -> str:
    for pattern in [r'\[(' + ID_PAT + r')\]', ID_PAT]:
        m = re.search(pattern, text)
        if m: return m.group(1) if '(' in pattern else m.group(0)
    return "INVALID_ID"

def main():
    print("="*60)
    print("  Generating Real Noisy Predictions on GPU (RTX 5070 Ti)")
    print("="*60)
    
    # 1. Load noisy test set
    if not os.path.exists(NOISY_TEST_PATH):
        print(f"Error: {NOISY_TEST_PATH} not found.")
        return
        
    with open(NOISY_TEST_PATH, 'r', encoding='utf-8') as f:
        test_samples = [json.loads(line) for line in f]
    print(f"Loaded {len(test_samples):,} noisy test samples.")
    
    # 2. Load model
    print("Loading model Llama-3-8B in 4-bit...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )
    
    base_model = AutoModelForCausalLM.from_pretrained(
        "unsloth/llama-3-8b-bnb-4bit",
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float16,
    )
    
    lora_path = str(cfg.LORA_MODEL)
    if os.path.exists(lora_path):
        print(f"Loading LoRA weights from {lora_path}...")
        model = PeftModel.from_pretrained(base_model, lora_path)
    else:
        print("WARNING: LoRA path not found. Using base model.")
        model = base_model
        
    model.eval()
    
    tokenizer = AutoTokenizer.from_pretrained("unsloth/llama-3-8b-bnb-4bit")
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Model successfully loaded on {DEVICE}.")
    
    # 3. Generate predictions in batches
    batch_size = 256
    results = []
    
    with torch.no_grad():
        for i in tqdm(range(0, len(test_samples), batch_size), desc="Inferencing"):
            batch = test_samples[i:i+batch_size]
            prompts = [PROMPT_TEMPLATE.format(instruction=item["instruction"]) for item in batch]
            
            inputs = tokenizer(
                prompts, return_tensors="pt", padding=True, truncation=True,
                max_length=2048 - 100
            ).to(DEVICE)
            
            input_len = inputs["input_ids"].shape[1]
            
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=False,
                num_beams=1,
                num_return_sequences=1,
                pad_token_id=tokenizer.eos_token_id,
            )
            
            new_tokens = outputs[:, input_len:]
            decoded = tokenizer.batch_decode(new_tokens, skip_special_tokens=True)
            
            for idx, text in enumerate(decoded):
                pred_id = parse_semantic_id(text)
                results.append({
                    "target_id": batch[idx]["target_id"],
                    "pred_id": pred_id,
                    "generated": text
                })
                
    # 4. Save results
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved actual predictions to {OUTPUT_CSV}")
    
    # Check a few samples
    print("\nCheck first 5 samples:")
    for idx, row in df.head(5).iterrows():
        print(f"Sample {idx+1}: Target: {row['target_id']} -> Pred: {row['pred_id']}")

if __name__ == '__main__':
    main()
