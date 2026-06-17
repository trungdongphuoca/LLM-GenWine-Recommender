"""
reformat_dataset.py
===================
Reformats the SFT dataset (train/val/test jsonl files) into a "Chain-of-Recommendation" format.
Instead of mapping directly to an ID, the model is trained to output a natural language
rationale (sommelier explanation) first, followed by the target cluster ID.

Output Format:
Rationale: [Professional sommelier explanation] -> Cluster: [C1-C2-C3]

Supports both English and Vietnamese rationale generation.
"""

import sys, os, json, re, argparse
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parents[1]))
import config as cfg
from tqdm import tqdm

def clean_desc_sentences(desc):
    """Split description into sentences and return the first two for sensory profile."""
    if not desc:
        return "", ""
    # Split by periods followed by spaces
    sentences = [s.strip() for s in re.split(r'\.(?=\s)|$', desc) if s.strip()]
    s1 = sentences[0] if len(sentences) > 0 else ""
    s2 = sentences[1] if len(sentences) > 1 else ""
    return s1, s2

def generate_rationale_en(instruction, thought_dict, description):
    """Generate a high-quality sommelier explanation in English."""
    user_analysis = thought_dict.get("user_analysis", {})
    grape = user_analysis.get("grape_preference", "wine")
    region = user_analysis.get("region_preference", "its origin")
    budget = user_analysis.get("budget", "your budget")
    candidate = thought_dict.get("candidate", "this selection")
    
    # Strip year from candidate name if present for cleaner flow
    candidate_clean = re.sub(r'\b\d{4}\b', '', candidate).replace("  ", " ").strip()
    
    s1, s2 = clean_desc_sentences(description)
    
    r1 = f"To match your preference for a {grape} from {region}, {candidate_clean} is an outstanding recommendation."
    r2 = f"This wine showcases a refined profile, highlighted by {s1.lower().rstrip('.')}."
    if s2:
        r3 = f"On the palate, it offers {s2.lower().rstrip('.')}, representing excellent value for a price of {budget}."
    else:
        r3 = f"This is a classic expression of {grape} from the region, aligning perfectly with your budget of {budget}."
        
    return f"{r1} {r2} {r3}"

def generate_rationale_vi(instruction, thought_dict, description):
    """Generate a high-quality sommelier explanation in Vietnamese."""
    user_analysis = thought_dict.get("user_analysis", {})
    grape = user_analysis.get("grape_preference", "rượu vang")
    region = user_analysis.get("region_preference", "nguồn gốc")
    budget = user_analysis.get("budget", "ngân sách")
    candidate = thought_dict.get("candidate", "chai vang này")
    
    candidate_clean = re.sub(r'\b\d{4}\b', '', candidate).replace("  ", " ").strip()
    
    s1, s2 = clean_desc_sentences(description)
    
    # Simple English-to-Vietnamese mapping for common grape types/categories for better readability
    grape_map = {
        "Pinot Noir": "vang đỏ Pinot Noir nhẹ nhàng",
        "Cabernet Sauvignon": "vang đỏ Cabernet Sauvignon đậm đà",
        "Chardonnay": "vang trắng Chardonnay thanh lịch",
        "Riesling": "vang trắng Riesling tinh tế",
        "Sauvignon Blanc": "vang trắng Sauvignon Blanc tươi mát",
        "Syrah": "vang đỏ Syrah mạnh mẽ",
        "Merlot": "vang đỏ Merlot mềm mại",
        "Sangiovese": "vang đỏ Sangiovese cổ điển",
        "Glera": "vang nổ Prosecco (Glera) tươi vui",
    }
    grape_vi = grape_map.get(grape, f"nho {grape}")
    
    # Translate basic regions/countries
    region_map = {
        "US": "Mỹ",
        "Italy": "Ý",
        "France": "Pháp",
        "Spain": "Tây Ban Nha",
        "Chile": "Chile",
        "Argentina": "Argentina",
        "Portugal": "Bồ Đào Nha",
        "Germany": "Đức",
        "Australia": "Úc",
        "New Zealand": "New Zealand",
        "South Africa": "Nam Phi"
    }
    region_vi = region_map.get(region, region)
    
    r1 = f"Để đáp ứng yêu cầu của bạn về dòng {grape_vi} từ {region_vi}, chai {candidate_clean} là lựa chọn vô cùng phù hợp."
    
    # Check if we should translate or use the tasting note descriptors
    # Since translation of descriptive adjectives is complex, we quote or present the original descriptors professionally
    if s1:
        r2 = f"Vang nổi bật với hương vị đặc trưng: '{s1.rstrip('.')}'."
    else:
        r2 = "Dòng vang này sở hữu cấu trúc cân bằng cùng hương thơm quyến rũ."
        
    if s2:
        r3 = f"Cảm nhận vòm miệng thể hiện rõ sự tinh tế qua '{s2.lower().rstrip('.')}', tạo nên điểm nhấn ấn tượng trong tầm giá {budget}."
    else:
        r3 = f"Đây là một đại diện xuất sắc phản ánh đúng phong cách thổ nhưỡng của vùng với giá hợp lý ({budget})."
        
    return f"{r1} {r2} {r3}"

def reformat_file(input_path, output_path, lang="en"):
    """Reads a JSONL file, reformats the response, and writes to output_path."""
    print(f"Reformatting {os.path.basename(input_path)} -> {os.path.basename(output_path)} (Lang: {lang})")
    
    # Write to a temporary file first to prevent truncation if input_path == output_path
    temp_output_path = output_path + ".tmp"
    
    count = 0
    with open(input_path, 'r', encoding='utf-8') as fin, open(temp_output_path, 'w', encoding='utf-8') as fout:
        for line in tqdm(fin):
            record = json.loads(line)
            
            # Extract target_id and slice it to get the C1-C2-C3 cluster ID
            target_id = record.get("target_id", "")
            if not target_id:
                # Fallback to parsing response for ID if target_id is empty
                match = re.search(r'\[(\d{2}-\d{2}-\d{2}-\d{3})\]', record.get("response", ""))
                target_id = match.group(1) if match else "00-00-00-000"
            
            # Cluster ID is C1-C2-C3 (first three parts)
            cluster_parts = target_id.split("-")[:3]
            cluster_id = "-".join(cluster_parts)
            
            # Parse thought block
            thought_str = record.get("thought", "{}")
            try:
                thought_dict = json.loads(thought_str)
            except Exception:
                thought_dict = {}
                
            # Extract description from original response
            orig_response = record.get("response", "")
            # The original response was "I suggest the [ID]. Description..."
            desc_match = re.sub(r'^I suggest the \[\d{2}-\d{2}-\d{2}-\d{3}\]\.\s*', '', orig_response)
            
            # Generate Rationale
            if lang == "vi":
                rationale = generate_rationale_vi(record["instruction"], thought_dict, desc_match)
            else:
                rationale = generate_rationale_en(record["instruction"], thought_dict, desc_match)
                
            # Build new output response format
            new_response = f"Rationale: {rationale} -> Cluster: {cluster_id}"
            
            # Update record
            record["response"] = new_response
            record["target_cluster"] = cluster_id  # Keep tracking cluster specifically
            
            fout.write(json.dumps(record, ensure_ascii=False) + '\n')
            count += 1
            
    # Rename temp file to output_path
    if os.path.exists(output_path):
        os.remove(output_path)
    os.rename(temp_output_path, output_path)
    
    print(f"Successfully processed {count:,} records.")

def main():
    parser = argparse.ArgumentParser(description="Reformat datasets for Chain-of-Recommendation SFT.")
    parser.add_argument("--lang", type=str, default="en", choices=["en", "vi"],
                        help="Language for the rationale (en or vi). Default: en")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite the original jsonl files instead of creating *_explainable.jsonl files.")
    args = parser.parse_args()
    
    # Set paths
    dataset_files = [
        (cfg.TRAIN_JSONL, "wine_train_explainable.jsonl" if not args.overwrite else "wine_train_130k.jsonl"),
        (cfg.VAL_JSONL, "wine_val_explainable.jsonl" if not args.overwrite else "wine_val_130k.jsonl"),
        (cfg.TEST_JSONL, "wine_test_explainable.jsonl" if not args.overwrite else "wine_test_130k.jsonl")
    ]
    
    for input_file, output_name in dataset_files:
        if not input_file.exists():
            print(f"Skipping {input_file.name} (file not found).")
            continue
            
        output_file = cfg.DATA_PROC / output_name
        reformat_file(str(input_file), str(output_file), lang=args.lang)
        
    print("\nDataset reformatting complete.")
    print("New SFT files saved in data/processed/ directory.")

if __name__ == "__main__":
    main()
