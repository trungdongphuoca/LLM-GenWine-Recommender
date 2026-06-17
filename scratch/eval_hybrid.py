import json
import pandas as pd
import numpy as np
import math

# Load catalog and test queries
cat = pd.read_csv('data/processed/wine_catalog_semantic.csv')
cat['_price'] = pd.to_numeric(cat['price'], errors='coerce').fillna(cat['price'].median())

# Extract predicted IDs from the greedy run
df_pred = pd.read_csv('results/constrained_eval_results.csv').iloc[:500]

with open('data/processed/wine_test_130k.jsonl') as f:
    test = [json.loads(line) for line in f][:500]

def extract_price(inst):
    import re
    m = re.search(r'\$\s*(\d+)', inst)
    return float(m.group(1)) if m else None

records = []
for i, item in enumerate(test):
    target_id = item['target_id']
    pred_id = df_pred.iloc[i]['pred_id']
    inst = item['instruction']
    
    # 1. Get predicted cluster C1-C2-C3
    if pd.isna(pred_id) or pred_id == 'INVALID_ID' or len(pred_id.split('-')) < 3:
        pred_cluster = ''
    else:
        pred_cluster = '-'.join(pred_id.split('-')[:3])
        
    # 2. Filter catalog to this cluster
    subset = cat[cat['Semantic_ID'].str.startswith(pred_cluster)].copy() if pred_cluster else pd.DataFrame()
    
    # 3. If subset is empty or too small, fall back to global popularity or price
    req_price = extract_price(inst)
    if len(subset) == 0:
        subset = cat.copy()
        
    # 4. Rank by price proximity
    if req_price is not None:
        subset['price_diff'] = np.abs(subset['_price'] - req_price)
        subset = subset.sort_values('price_diff')
    else:
        subset = subset.sample(frac=1, random_state=42)
        
    ret = subset['Semantic_ID'].tolist()[:10]
    
    # Calculate metrics
    r1 = 1.0 if target_id in ret[:1] else 0.0
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

df_res = pd.DataFrame(records)
print('=== HYBRID CLUSTER-FILTERED PRICE RE-RANKING METRICS ===')
print(f'Recall@1 : {df_res["r1"].mean()*100:.2f}%')
print(f'Recall@5 : {df_res["r5"].mean()*100:.2f}%')
print(f'Recall@10: {df_res["r10"].mean()*100:.2f}%')
print(f'NDCG@10  : {df_res["ndcg10"].mean()*100:.2f}%')
print(f'MRR      : {df_res["mrr"].mean()*100:.2f}%')
