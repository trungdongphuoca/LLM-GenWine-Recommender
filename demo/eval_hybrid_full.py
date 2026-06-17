"""
Full Hybrid Pipeline Evaluation on the Entire Test Set (N=12,991)
Evaluates Proposed Model (TIGER + Price Rerank) on the full test split.
"""
import sys, json, re, time, math
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parents[1]
CATALOG_PATH = ROOT / 'data/processed/wine_catalog_semantic.csv'
TEST_PATH    = ROOT / 'data/processed/wine_test_130k.jsonl'
PREDS_PATH   = ROOT / 'results/constrained_eval_results.csv'

print("=" * 65)
print("PROPOSED MODEL FULL EVALUATION  —  N = 12,991")
print("=" * 65)

# ── Load catalog ──────────────────────────────────────────────
print("Loading catalog...")
cat = pd.read_csv(CATALOG_PATH, usecols=['Semantic_ID', 'price'], dtype=str).fillna('')
# Convert price to numeric
cat['_price'] = pd.to_numeric(cat['price'], errors='coerce')
median_price = cat['_price'].median()
cat['_price'] = cat['_price'].fillna(median_price)

# Pre-group catalog by cluster prefix to speed up filtering
cat_ids = cat['Semantic_ID'].tolist()
cat_prices = cat['_price'].values

# Create a mapping from cluster prefix (C1-C2-C3) to array indices
from collections import defaultdict
cluster_to_indices = defaultdict(list)
for i, sid in enumerate(cat_ids):
    parts = sid.split('-')
    if len(parts) >= 3:
        prefix = '-'.join(parts[:3])
        cluster_to_indices[prefix].append(i)

# ── Load predictions and test set ──────────────────────────────
print("Loading predictions and test set...")
df_pred = pd.read_csv(PREDS_PATH)
with open(TEST_PATH, encoding='utf-8') as f:
    test = [json.loads(line) for line in f]

N = len(test)
print(f"Loaded {N:,} test cases and {len(df_pred):,} predictions.")

# Check matching lengths
if N != len(df_pred):
    print(f"WARNING: Length mismatch! N={N}, Predictions={len(df_pred)}")
    N = min(N, len(df_pred))

# ── Run Evaluation ─────────────────────────────────────────────
print("\nRunning Price Reranking on all samples...")
t0 = time.time()

records = []
def extract_price(inst):
    m = re.search(r'\$\s*(\d+)', inst)
    return float(m.group(1)) if m else None

# Pre-convert catalog semantic IDs to np.array for fast indexing
cat_ids_arr = np.array(cat_ids)

for i in range(N):
    item = test[i]
    target_id = item['target_id']
    pred_id = df_pred.iloc[i]['pred_id']
    inst = item['instruction']
    
    if pd.isna(pred_id) or pred_id == 'INVALID_ID' or len(str(pred_id).split('-')) < 3:
        pred_cluster = ''
    else:
        pred_cluster = '-'.join(str(pred_id).split('-')[:3])
    
    # Get cluster indices
    indices = cluster_to_indices.get(pred_cluster, [])
    
    req_price = extract_price(inst)
    
    if len(indices) == 0:
        # Fallback to whole catalog
        indices = np.arange(len(cat))
    else:
        indices = np.array(indices)
        
    if req_price is not None:
        sub_prices = cat_prices[indices]
        price_diff = np.abs(sub_prices - req_price)
        # Sort indices by price difference
        sorted_local_idx = np.argsort(price_diff)
        ranked_global_idx = indices[sorted_local_idx[:10]]
    else:
        # Just take first 10
        ranked_global_idx = indices[:10]
        
    ret = cat_ids_arr[ranked_global_idx].tolist()
    
    # Metrics
    r1 = 1.0 if len(ret) > 0 and ret[0] == target_id else 0.0
    r5 = 1.0 if target_id in ret[:5] else 0.0
    r10 = 1.0 if target_id in ret[:10] else 0.0
    
    mrr = 0.0
    ndcg10 = 0.0
    for rank, pid in enumerate(ret[:10]):
        if pid == target_id:
            mrr = 1.0 / (rank + 1)
            ndcg10 = 1.0 / math.log2(rank + 2)
            break
            
    records.append({'r1': r1, 'r5': r5, 'r10': r10, 'ndcg10': ndcg10, 'mrr': mrr})
    
    if (i+1) % 4000 == 0:
        print(f"  Processed {i+1:,}/{N:,} ({ (i+1)/N*100 :.0f}%)")

t_elapsed = time.time() - t0
df_res = pd.DataFrame(records)

m_hybrid = {
    'Recall@1':  round(df_res["r1"].mean()*100, 3),
    'Recall@5':  round(df_res["r5"].mean()*100, 3),
    'Recall@10': round(df_res["r10"].mean()*100, 3),
    'NDCG@10':   round(df_res["ndcg10"].mean()*100, 3),
    'MRR':       round(df_res["mrr"].mean()*100, 3),
    'Latency_ms': 15703.0 # Hardcoded CPU latency or 2277.5 for GPU
}

print('\n' + '=' * 60)
print('PROPOSED HYBRID MODEL METRICS ON FULL TEST SET (N=12,991)')
print('=' * 60)
print(f'Recall@1 : {m_hybrid["Recall@1"]}%')
print(f'Recall@5 : {m_hybrid["Recall@5"]}%')
print(f'Recall@10: {m_hybrid["Recall@10"]}%')
print(f'NDCG@10  : {m_hybrid["NDCG@10"]}%')
print(f'MRR      : {m_hybrid["MRR"]}%')
print(f'Done in {t_elapsed:.2f}s | Average {t_elapsed/N*1000:.2f}ms per reranking')
print('=' * 60 + '\n')

# Save to hybrid full summary
out_summary = ROOT / 'results/hybrid_summary_full.csv'
pd.DataFrame([m_hybrid]).to_csv(out_summary, index=False)
print(f"✅ Saved to: {out_summary}")
