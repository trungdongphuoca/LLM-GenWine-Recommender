import json
import pandas as pd
import numpy as np
import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load catalog and test queries
cat = pd.read_csv('data/processed/wine_catalog_semantic.csv')
cat['_price'] = pd.to_numeric(cat['price'], errors='coerce').fillna(cat['price'].median())

# Extract predicted IDs from the greedy run
df_pred = pd.read_csv('results/constrained_eval_results.csv').iloc[:500]

with open('data/processed/wine_test_130k.jsonl') as f:
    test = [json.loads(line) for line in f][:500]

# Fit a TF-IDF vectorizer on the catalog doc_text
print("Fitting TF-IDF on catalog...")
vectorizer = TfidfVectorizer(max_features=50000, stop_words='english')
tfidf_matrix = vectorizer.fit_transform(cat['doc_text'])

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
    
    # 3. If subset is empty, fall back to global catalog
    if len(subset) == 0:
        subset = cat.copy()
        
    # 4. TF-IDF similarity within subset
    sub_tfidf = vectorizer.transform(subset['doc_text'])
    query_tfidf = vectorizer.transform([inst])
    tfidf_scores = cosine_similarity(query_tfidf, sub_tfidf)[0]
    
    # 5. Price proximity score
    req_price = extract_price(inst)
    if req_price is not None:
        price_dist = np.abs(subset['_price'].values - req_price)
        max_dist = price_dist.max() + 1e-9
        price_scores = 1.0 - price_dist / max_dist
    else:
        price_scores = np.ones(len(subset))
        
    # Combined score (weighted: 50% price, 50% TF-IDF description similarity)
    subset['score'] = 0.5 * price_scores + 0.5 * tfidf_scores
    subset = subset.sort_values('score', ascending=False)
    
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
print('=== HYBRID CLUSTER-FILTERED + TF-IDF + PRICE METRICS ===')
print(f'Recall@1 : {df_res["r1"].mean()*100:.2f}%')
print(f'Recall@5 : {df_res["r5"].mean()*100:.2f}%')
print(f'Recall@10: {df_res["r10"].mean()*100:.2f}%')
print(f'NDCG@10  : {df_res["ndcg10"].mean()*100:.2f}%')
print(f'MRR      : {df_res["mrr"].mean()*100:.2f}%')
