"""
Full Test Set Evaluation (N=12,991)
Evaluates: BM25, TF-IDF, Struct-Filter BM25+, Struct-Filter TF-IDF, BM25 Enhanced
on the full wine_test_130k.jsonl split.

For TIGER (LLM): reports N=500 pre-computed results from constrained_eval_beam10_500.csv

Run: .venv\Scripts\python.exe demo\eval_full_test.py
"""
import sys, json, re, time
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi

ROOT = Path(__file__).parents[1]
CATALOG_PATH = ROOT / 'data/processed/wine_catalog_semantic.csv'
TEST_PATH    = ROOT / 'data/processed/wine_test_130k.jsonl'

print("=" * 60)
print("FULL TEST SET EVALUATION  —  N = 12,991")
print("=" * 60)

# ── Load catalog ──────────────────────────────────────────────
print("\n[1/4] Loading catalog (130K)...")
cat = pd.read_csv(CATALOG_PATH,
    usecols=['title', 'variety', 'country', 'price', 'description',
             'Semantic_ID', 'Semantic_ID_Cluster', 'doc_text'],
    dtype=str).fillna('')

id2idx = {row['Semantic_ID']: i for i, row in cat.iterrows()}

# ── Build indexes ─────────────────────────────────────────────
print("[2/4] Building indexes...")
t0 = time.time()
tfidf = TfidfVectorizer(max_features=8000, ngram_range=(1, 2))
tfidf_mat = tfidf.fit_transform(cat['doc_text'])
print(f"  TF-IDF: {time.time()-t0:.1f}s")

t0 = time.time()
corpus = [t.split() for t in cat['doc_text'].tolist()]
bm25   = BM25Okapi(corpus)
print(f"  BM25  : {time.time()-t0:.1f}s")

# ── Load test set ─────────────────────────────────────────────
print("[3/4] Loading test set...")
test_data = []
with open(TEST_PATH, encoding='utf-8') as f:
    for line in f:
        test_data.append(json.loads(line))
print(f"  Loaded {len(test_data):,} test cases")

# ── Parse instruction ─────────────────────────────────────────
def parse_instruction(txt):
    v = re.search(r'Recommend a (.+?) from', txt)
    c = re.search(r'from (.+?) that', txt)
    p = re.search(r'around \$([0-9]+(?:\.[0-9]+)?)', txt)
    return (
        v.group(1).strip().lower() if v else '',
        c.group(1).strip().lower() if c else '',
        float(p.group(1)) if p else 0.0
    )

# ── Metrics ───────────────────────────────────────────────────
def calc_metrics(results_list, targets_list):
    """results_list: list of [ranked_ids], targets_list: list of target_id"""
    r1 = r5 = r10 = ndcg10 = mrr = 0.0
    n = len(targets_list)
    for preds, tgt in zip(results_list, targets_list):
        hit1  = 1 if preds[:1]  and preds[0]  == tgt else 0
        hit5  = 1 if tgt in preds[:5]  else 0
        hit10 = 1 if tgt in preds[:10] else 0
        r1  += hit1; r5 += hit5; r10 += hit10
        # NDCG@10
        ndcg = 0.0
        for k, p in enumerate(preds[:10]):
            if p == tgt:
                ndcg = 1.0 / np.log2(k + 2); break
        ndcg10 += ndcg
        # MRR
        for k, p in enumerate(preds[:10]):
            if p == tgt:
                mrr += 1.0 / (k + 1); break
    return {
        'Recall@1':  round(r1/n*100, 3),
        'Recall@5':  round(r5/n*100, 3),
        'Recall@10': round(r10/n*100, 3),
        'NDCG@10':   round(ndcg10/n*100, 3),
        'MRR':       round(mrr/n*100, 3),
    }

# ── Search functions ──────────────────────────────────────────
def rank_bm25(query, k=10):
    tokens = query.lower().split()
    scores = bm25.get_scores(tokens)
    ranked = np.argsort(-scores)[:k]
    return [cat.iloc[i]['Semantic_ID'] for i in ranked]

def rank_tfidf(query, k=10):
    q = tfidf.transform([query.lower()])
    sims = cosine_similarity(q, tfidf_mat).flatten()
    ranked = np.argsort(-sims)[:k]
    return [cat.iloc[i]['Semantic_ID'] for i in ranked]

def rank_struct_bm25(variety, country, price, k=10):
    """Filter by variety/country, then BM25 within, then price rerank."""
    mask = pd.Series([True]*len(cat))
    if variety:
        mask &= cat['variety'].str.lower().str.contains(variety[:10], na=False)
    if country:
        mask &= cat['country'].str.lower().str.contains(country[:8], na=False)
    sub = cat[mask].copy()
    if len(sub) == 0:
        sub = cat.copy()
    tokens = (variety + ' ' + country).split()
    sub_doc = sub['doc_text'].tolist()
    sub_bm25 = BM25Okapi([d.split() for d in sub_doc])
    scores = sub_bm25.get_scores(tokens)
    ranked_idx = np.argsort(-scores)[:50]
    # Price rerank
    if price > 0:
        cands = [(sub.iloc[i]['Semantic_ID'],
                  abs(float(sub.iloc[i]['price']) - price) if sub.iloc[i]['price'].replace('.','',1).isdigit() else 999)
                 for i in ranked_idx]
        cands.sort(key=lambda x: x[1])
        return [c[0] for c in cands[:k]]
    return [sub.iloc[i]['Semantic_ID'] for i in ranked_idx[:k]]

def rank_bm25_enhanced(instruction, variety, country, price, k=10):
    """BM25 on full doc + structural filter."""
    query = f"{variety} {country} wine"
    base = rank_bm25(query, k=100)
    # Filter by variety/country if matches
    filtered = []
    for sid in base:
        if sid not in id2idx: continue
        r = cat.iloc[id2idx[sid]]
        v_ok = not variety or variety[:6] in r['variety'].lower()
        c_ok = not country or country[:5] in r['country'].lower()
        if v_ok and c_ok:
            filtered.append(sid)
    if len(filtered) < k:
        filtered = base
    # Price rerank
    if price > 0:
        def pdist(sid):
            r = cat.iloc[id2idx.get(sid,0)]
            try: return abs(float(r['price']) - price)
            except: return 999
        filtered = sorted(filtered[:50], key=pdist)
    return filtered[:k]

# ── Run evaluation ────────────────────────────────────────────
print("\n[4/4] Running evaluation on N=12,991...\n")
methods = ['BM25', 'TF-IDF', 'Struct-Filter BM25', 'BM25 Enhanced']
all_preds = {m: [] for m in methods}
targets = []

TOTAL = len(test_data)
LOG_INTERVAL = 500

t_start = time.time()
for idx, sample in enumerate(test_data):
    if idx % LOG_INTERVAL == 0 and idx > 0:
        elapsed = time.time() - t_start
        eta = elapsed / idx * (TOTAL - idx)
        print(f"  Progress: {idx:,}/{TOTAL:,} ({idx/TOTAL*100:.1f}%) | ETA: {eta:.0f}s")

    instr = sample['instruction']
    target = sample['target_id']
    targets.append(target)

    variety, country, price = parse_instruction(instr)
    query = f"{variety} {country} wine"

    all_preds['BM25'].append(rank_bm25(query))
    all_preds['TF-IDF'].append(rank_tfidf(query))
    all_preds['Struct-Filter BM25'].append(rank_struct_bm25(variety, country, price))
    all_preds['BM25 Enhanced'].append(rank_bm25_enhanced(instr, variety, country, price))

total_elapsed = time.time() - t_start
print(f"\n  Done! Total time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")

# ── Compute metrics ───────────────────────────────────────────
print("\n" + "=" * 60)
print("RESULTS  —  Full Test Set (N=12,991)")
print("=" * 60)

rows = []
for method in methods:
    m = calc_metrics(all_preds[method], targets)
    m['Method'] = method
    m['N'] = TOTAL
    rows.append(m)

# Add TIGER from pre-computed N=500
tiger_df = pd.read_csv(ROOT / 'results/constrained_eval_beam10_500.csv')
rows.append({
    'Method': 'TIGER + Price Rerank (Proposed)',
    'Recall@1':  round(0.016*100, 3),
    'Recall@5':  round(0.044*100, 3),
    'Recall@10': round(0.054*100, 3),
    'NDCG@10':   round(0.033247*100, 3),
    'MRR':       round(0.026744*100, 3),
    'N': 500,  # note
})

result_df = pd.DataFrame(rows)[['Method', 'N', 'Recall@1', 'Recall@5', 'Recall@10', 'NDCG@10', 'MRR']]
print(result_df.to_string(index=False))

# Save
out_path = ROOT / 'results/full_test_eval_12991.csv'
result_df.to_csv(out_path, index=False, encoding='utf-8-sig')
print(f"\n✅ Saved to: {out_path}")
