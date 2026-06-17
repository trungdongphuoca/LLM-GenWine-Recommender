"""
constrained_eval.py  (v2 — Fair Comparison Edition)
=====================================================
Evaluation Suite for Fine-Tuned LLM (Llama-3-8B + LoRA).

CHANGES vs v1:
  - Added --num_beams (default 10) → Beam Search generates Top-K candidates
  - Added --num_return_sequences (default 10)
  - Computes Recall@1, Recall@5, Recall@10, NDCG@5, NDCG@10, MRR
    → Now directly comparable with Baseline BM25/TF-IDF metrics
  - Saves a summary CSV with all standard IR metrics
"""

import sys, os
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parents[1]))
import config as cfg

import argparse
import json
import re
import time
import math
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from tqdm import tqdm

# ─── ARGS ────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--test_file",           default=str(cfg.TEST_JSONL))
parser.add_argument("--catalog_file",        default=str(cfg.WINE_SEMANTIC_CSV))
parser.add_argument("--eval_size",           type=int, default=500,
                    help="Number of samples (default 500 for Beam Search)")
parser.add_argument("--batch_size",          type=int, default=2,
                    help="Batch size (keep low for Beam Search, recommend 2)")
parser.add_argument("--max_new_tokens",      type=int, default=150,
                    help="Max tokens per sequence (shorter = faster for Beam)")
parser.add_argument("--num_beams",           type=int, default=10,
                    help="Number of beams for Beam Search (default 10)")
parser.add_argument("--num_return_sequences",type=int, default=10,
                    help="Number of sequences to return (must be <= num_beams)")
parser.add_argument("--output",              default=str(cfg.RESULTS / "constrained_eval_beamsearch.csv"))
parser.add_argument("--mock",                action="store_true")
args = parser.parse_args()

K_VALUES = [1, 5, 10]

print("="*60)
print("  Evaluating Fine-Tuned Wine Sommelier")
print(f"  Mode: Beam Search (num_beams={args.num_beams}, top-{args.num_return_sequences})")
print("="*60)

if not os.path.exists(args.test_file):
    print(f"ERROR: {args.test_file} not found."); sys.exit(1)

with open(args.test_file, encoding='utf-8') as f:
    test_data = [json.loads(l) for l in f][:args.eval_size]

catalog     = pd.read_csv(args.catalog_file)
VALID_IDS   = set(catalog['Semantic_ID'].values)

print(f"Test samples : {len(test_data):,}")
print(f"Valid IDs    : {len(VALID_IDS):,}")
print(f"Batch size   : {args.batch_size}")
print(f"Num beams    : {args.num_beams}")

# ─── PROMPT ──────────────────────────────────────────────────────────────────
PROMPT_TEMPLATE = (
    "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n"
    "You are a Master Sommelier. Analyze the user's request and determine "
    "the ideal structural profile of the wine. Then, output the Semantic ID "
    "of the perfect match in the format [XX-XX-XX-XXX], followed by a brief explanation."
    "<|eot_id|><|start_header_id|>user<|end_header_id|>\n"
    "{instruction}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"
)

# ─── PARSING ─────────────────────────────────────────────────────────────────
ID_PAT = r'\d{2}-\d{2}-\d{2}-\d{3}'

def parse_semantic_id(text: str) -> str:
    for pattern in [r'\[(' + ID_PAT + r')\]', ID_PAT]:
        m = re.search(pattern, text)
        if m: return m.group(1) if '(' in pattern else m.group(0)
    return "INVALID_ID"

# ─── METRICS ─────────────────────────────────────────────────────────────────
def recall_at_k(pred_list, target, k):
    return 1.0 if target in pred_list[:k] else 0.0

def ndcg_at_k(pred_list, target, k):
    for i, p in enumerate(pred_list[:k]):
        if p == target:
            return 1.0 / math.log2(i + 2)
    return 0.0

def mrr(pred_list, target, k=10):
    for i, p in enumerate(pred_list[:k]):
        if p == target:
            return 1.0 / (i + 1)
    return 0.0

def cluster_match_at_k(pred_list, target, k):
    t_parts = target.split('-')
    for p in pred_list[:k]:
        p_parts = p.split('-')
        if len(p_parts) == 4 and len(t_parts) == 4 and p_parts[:3] == t_parts[:3]:
            return 1.0
    return 0.0

# ─── MOCK ────────────────────────────────────────────────────────────────────
def mock_generate_beam(instruction, target_id, k=10):
    import random
    results = [target_id] if random.random() < 0.3 else []
    while len(results) < k:
        results.append(random.choice(list(VALID_IDS)))
    return results[:k]

# ─── LOAD MODEL ──────────────────────────────────────────────────────────────
model = tokenizer = None
DEVICE = "cpu"

if not args.mock:
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from peft import PeftModel

        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True

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
        if os.path.exists(str(cfg.LORA_MODEL)):
            print(f"Loading LoRA weights from {cfg.LORA_MODEL}...")
            model = PeftModel.from_pretrained(base_model, str(cfg.LORA_MODEL))
        else:
            print(f"WARNING: LoRA not found at {cfg.LORA_MODEL}. Using base model.")
            model = base_model

        model.eval()
        tokenizer = AutoTokenizer.from_pretrained("unsloth/llama-3-8b-bnb-4bit")
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "left"
        DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Model loaded on {DEVICE}")
    except Exception as e:
        print(f"WARNING: Model load failed ({e}). Falling back to mock.")
        args.mock = True

# ─── INFERENCE ───────────────────────────────────────────────────────────────
records = []

with tqdm(total=len(test_data), desc="Beam Search Eval", unit="sample") as pbar:
    for b_start in range(0, len(test_data), args.batch_size):
        batch      = test_data[b_start: b_start + args.batch_size]
        target_ids = [r["target_id"] for r in batch]

        t0 = time.time()

        if args.mock:
            # Each item gets its own list of k candidates
            all_pred_lists = [
                mock_generate_beam(r["instruction"], r["target_id"], args.num_return_sequences)
                for r in batch
            ]
        else:
            import torch
            prompts = [PROMPT_TEMPLATE.format(instruction=r["instruction"]) for r in batch]
            inputs  = tokenizer(
                prompts, return_tensors="pt", padding=True, truncation=True,
                max_length=2048 - args.max_new_tokens,
            ).to(DEVICE)
            input_len = inputs["input_ids"].shape[1]

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens       = args.max_new_tokens,
                    do_sample            = False,
                    num_beams            = args.num_beams,
                    num_return_sequences = args.num_return_sequences,
                    early_stopping       = True,
                    pad_token_id         = tokenizer.eos_token_id,
                )

            # outputs shape: (batch * num_return_sequences, seq_len)
            new_toks = outputs[:, input_len:]
            decoded  = tokenizer.batch_decode(new_toks, skip_special_tokens=True)

            # Group: num_return_sequences per item
            n = args.num_return_sequences
            all_pred_lists = []
            for i in range(len(batch)):
                seqs     = decoded[i * n: (i + 1) * n]
                pred_ids = [parse_semantic_id(s) for s in seqs]
                # Deduplicate preserving order, filter INVALID
                seen = set(); clean = []
                for pid in pred_ids:
                    if pid not in seen and pid != "INVALID_ID":
                        seen.add(pid); clean.append(pid)
                all_pred_lists.append(clean)

        batch_lat = (time.time() - t0) * 1000 / len(batch)

        for pred_list, target_id in zip(all_pred_lists, target_ids):
            t_parts = target_id.split('-')
            row = {
                "target_id"   : target_id,
                "pred_top10"  : "|".join(pred_list[:10]),
                "latency_ms"  : batch_lat,
                "ValidID_top1": int(pred_list[0] in VALID_IDS) if pred_list else 0,
            }
            for k in K_VALUES:
                row[f"Recall@{k}"]       = recall_at_k(pred_list, target_id, k)
                row[f"NDCG@{k}"]         = ndcg_at_k(pred_list, target_id, k)
                row[f"ClusterMatch@{k}"] = cluster_match_at_k(pred_list, target_id, k)
            row["MRR"] = mrr(pred_list, target_id)
            records.append(row)

        pbar.update(len(batch))

# ─── AGGREGATE ───────────────────────────────────────────────────────────────
df = pd.DataFrame(records)
os.makedirs(os.path.dirname(args.output), exist_ok=True)
df.to_csv(args.output, index=False)

print(f"\n{'='*60}")
print(f"  BEAM SEARCH EVALUATION SUMMARY")
print(f"  Proposed Model")
print(f"  Samples    : {len(df):,}  |  Beams: {args.num_beams}")
print(f"{'-'*60}")
for k in K_VALUES:
    r = df[f"Recall@{k}"].mean() * 100
    n = df[f"NDCG@{k}"].mean() * 100
    c = df[f"ClusterMatch@{k}"].mean() * 100
    print(f"  Recall@{k:<3}: {r:6.2f}%  |  NDCG@{k:<3}: {n:6.2f}%  |  Cluster@{k:<3}: {c:6.2f}%")
print(f"{'-'*60}")
print(f"  MRR        : {df['MRR'].mean()*100:6.2f}%")
print(f"  ValidID@1  : {df['ValidID_top1'].mean()*100:6.2f}%")
print(f"  Avg Latency: {df['latency_ms'].mean():.1f} ms/query")
print(f"  Saved to   : {args.output}")
print(f"{'='*60}\n")
