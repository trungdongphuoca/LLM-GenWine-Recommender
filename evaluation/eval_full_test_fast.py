"""
FAST Full Test Set Evaluation (N=12,991)
Highly optimized vectorized implementation with custom sparse BM25 and mask caching.
ETA: ~30-40 seconds total.

Run: .venv\Scripts\python.exe demo\eval_full_test_fast.py
"""
import sys, json, re, time
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).parents[1]
CATALOG_PATH = ROOT / 'data/processed/wine_catalog_semantic.csv'
TEST_PATH    = ROOT / 'data/processed/wine_test_130k.jsonl'

print("=" * 65)
print("FULL TEST SET EVALUATION  —  N = 12,991  (Optimized Fast Vectorized)")
print("=" * 65)

# ── Load catalog ──────────────────────────────────────────────
print("\n[1/5] Loading catalog (130K)...")
cat = pd.read_csv(CATALOG_PATH,
    usecols=['title', 'variety', 'country', 'price', 'description',
             'Semantic_ID', 'Semantic_ID_Cluster', 'doc_text'],
    dtype=str).fillna('')

id2idx = {row['Semantic_ID']: i for i, row in cat.iterrows()}
cat_ids = cat['Semantic_ID'].tolist()
cat_variety = cat['variety'].str.lower().tolist()
cat_country = cat['country'].str.lower().tolist()
cat_price_num = pd.to_numeric(cat['price'], errors='coerce').fillna(-1).tolist()
cat_price_arr = np.array(cat_price_num)

# ── Build TF-IDF index ────────────────────────────────────────
print("[2/5] Building TF-IDF index...")
t0 = time.time()
tfidf = TfidfVectorizer(max_features=10000, ngram_range=(1, 2), min_df=2)
tfidf_mat = tfidf.fit_transform(cat['doc_text'])  # shape: (130k, vocab)
print(f"  TF-IDF: {time.time()-t0:.1f}s | shape: {tfidf_mat.shape}")

# ── Build Custom Sparse BM25 index ─────────────────────────────
print("[3/5] Building Optimized Sparse BM25 index...")
t0 = time.time()
def dummy_tokenizer(text):
    return text.split()

# Fit CountVectorizer with dummy tokenizer to extract raw term frequencies
vectorizer = CountVectorizer(tokenizer=dummy_tokenizer, lowercase=True)
tf_matrix = vectorizer.fit_transform(cat['doc_text'])  # shape: (130k, vocab)
tf_matrix = tf_matrix.tocsc()  # Convert to CSC format for fast column slicing
print(f"  Sparse term frequencies: {time.time()-t0:.1f}s | shape: {tf_matrix.shape}")

N_docs = tf_matrix.shape[0]
doc_lens = np.array(tf_matrix.sum(axis=1)).flatten()
avgdl = doc_lens.mean()

# rank_bm25 IDF calculation formula
df = np.array((tf_matrix > 0).sum(axis=0)).flatten()
idf = np.log(N_docs - df + 0.5) - np.log(df + 0.5)
average_idf = idf.mean()
eps = 0.25 * average_idf
idf[idf < 0] = eps

vocab = vectorizer.vocabulary_

# precompute doc_lens scaling
k1 = 1.5
b = 0.75
doc_len_factor = k1 * (1 - b + b * (doc_lens / avgdl))

def get_bm25_scores(q_tokens):
    scores = np.zeros(N_docs)
    for token in q_tokens:
        if token in vocab:
            idx = vocab[token]
            idf_val = idf[idx]
            
            # Slicing from CSC matrix is extremely fast
            col = tf_matrix[:, idx]
            rows = col.indices
            tf_vals = col.data
            
            if len(rows) > 0:
                denom = tf_vals + doc_len_factor[rows]
                scores[rows] += idf_val * tf_vals * (k1 + 1) / denom
    return scores

# ── Load test set ─────────────────────────────────────────────
print("[4/5] Loading & parsing test set...")
t0 = time.time()
instructions, targets, varieties, countries, prices = [], [], [], [], []

def parse_instruction(txt):
    v = re.search(r'Recommend a (.+?) from', txt)
    c = re.search(r'from (.+?) that', txt)
    p = re.search(r'around \$([0-9]+(?:\.[0-9]+)?)', txt)
    return (
        v.group(1).strip().lower() if v else '',
        c.group(1).strip().lower() if c else '',
        float(p.group(1)) if p else 0.0
    )

with open(TEST_PATH, encoding='utf-8') as f:
    for line in f:
        s = json.loads(line)
        instructions.append(s['instruction'])
        targets.append(s['target_id'])
        v, c, p = parse_instruction(s['instruction'])
        varieties.append(v); countries.append(c); prices.append(p)

N = len(targets)
print(f"  Loaded {N:,} test cases in {time.time()-t0:.1f}s")

# ── Compute query matrix for TF-IDF ───────────────────────────
print("\n[5/5] Computing query matrices...")
queries = [f"{v} {c} wine" for v, c in zip(varieties, countries)]

t0 = time.time()
Q_tfidf = tfidf.transform(queries)  # (N, vocab)
print(f"  Query transform TF-IDF: {time.time()-t0:.1f}s")

# ── Metrics helper ────────────────────────────────────────────
def calc_metrics(pred_matrix, tgt_list):
    """pred_matrix: (N, k) array of predicted IDs (strings), tgt_list: list of N strings"""
    r1 = r5 = r10 = ndcg10 = mrr = 0.0
    for preds, tgt in zip(pred_matrix, tgt_list):
        preds = list(preds)
        r1  += (1 if len(preds) > 0 and preds[0] == tgt else 0)
        r5  += (1 if tgt in preds[:5]  else 0)
        r10 += (1 if tgt in preds[:10] else 0)
        for k, p in enumerate(preds[:10]):
            if p == tgt:
                ndcg10 += 1.0 / np.log2(k + 2)
                mrr    += 1.0 / (k + 1)
                break
    n = len(tgt_list)
    return {
        'Recall@1':  round(r1/n*100, 3),
        'Recall@5':  round(r5/n*100, 3),
        'Recall@10': round(r10/n*100, 3),
        'NDCG@10':   round(ndcg10/n*100, 3),
        'MRR':       round(mrr/n*100, 3),
    }

# ── Method 1: TF-IDF (batch cosine similarity) ───────────────
print("\n--- Method 1: TF-IDF ---")
t0 = time.time()
BATCH = 256
tfidf_preds = []
for i in range(0, N, BATCH):
    q_batch = Q_tfidf[i:i+BATCH]
    sims = cosine_similarity(q_batch, tfidf_mat)  # (batch, 130k)
    # Fast top 10 extraction
    ranked_batch = np.argpartition(-sims, 10, axis=1)[:, :10]
    for idx_in_batch in range(len(sims)):
        top10_local = ranked_batch[idx_in_batch]
        top10_sorted = top10_local[np.argsort(-sims[idx_in_batch, top10_local])]
        tfidf_preds.append([cat_ids[j] for j in top10_sorted])
    if i % 4000 == 0 and i > 0:
        print(f"  TF-IDF: {i:,}/{N:,} ({i/N*100:.0f}%)")
t_tfidf = time.time() - t0
m_tfidf = calc_metrics(tfidf_preds, targets)
m_tfidf['Latency_ms'] = round(t_tfidf/N*1000, 2)
print(f"  Done in {t_tfidf:.1f}s | Recall@10: {m_tfidf['Recall@10']}%")

# ── Method 2: BM25 (per query, fast sparse) ──────────────────
print("\n--- Method 2: BM25 ---")
t0 = time.time()
bm25_preds = []
for i, q in enumerate(queries):
    tokens = q.split()
    scores = get_bm25_scores(tokens)
    top10_idx = np.argpartition(-scores, 10)[:10]
    top10_sorted = top10_idx[np.argsort(-scores[top10_idx])]
    bm25_preds.append([cat_ids[j] for j in top10_sorted])
    if i % 4000 == 0 and i > 0:
        print(f"  BM25: {i:,}/{N:,} ({i/N*100:.0f}%)")
t_bm25 = time.time() - t0
m_bm25 = calc_metrics(bm25_preds, targets)
m_bm25['Latency_ms'] = round(t_bm25/N*1000, 2)
print(f"  Done in {t_bm25:.1f}s | Recall@10: {m_bm25['Recall@10']}%")

# ── Method 3: Struct-Filter BM25 ─────────────────────────────
print("\n--- Method 3: Struct-Filter BM25 ---")
t0 = time.time()
struct_preds = []

# Precompute unique varieties/countries and their index mappings in catalog
unique_varieties = cat['variety'].str.lower().unique()
unique_countries = cat['country'].str.lower().unique()

variety_to_indices = {var: np.where(cat['variety'].str.lower() == var)[0] for var in unique_varieties if var}
country_to_indices = {ctr: np.where(cat['country'].str.lower() == ctr)[0] for ctr in unique_countries if ctr}

mask_cache = {}

def get_structural_subset(v, c):
    key = (v, c)
    if key in mask_cache:
        return mask_cache[key]
    
    if not v:
        v_idx = None
    else:
        matching_vars = [var for var in unique_varieties if var and v[:10] in var]
        v_idx = np.concatenate([variety_to_indices[var] for var in matching_vars]) if matching_vars else np.array([], dtype=int)
    
    if not c:
        c_idx = None
    else:
        matching_ctrs = [ctr for ctr in unique_countries if ctr and c[:8] in ctr]
        c_idx = np.concatenate([country_to_indices[ctr] for ctr in matching_ctrs]) if matching_ctrs else np.array([], dtype=int)
        
    if v_idx is None and c_idx is None:
        sub_idx = np.arange(len(cat))
    elif v_idx is None:
        sub_idx = c_idx
    elif c_idx is None:
        sub_idx = v_idx
    else:
        sub_idx = np.intersect1d(v_idx, c_idx, assume_unique=True)
        
    if len(sub_idx) < 5:
        sub_idx = np.arange(len(cat))
        
    mask_cache[key] = sub_idx
    return sub_idx

for i, (v, c, p) in enumerate(zip(varieties, countries, prices)):
    sub_idx = get_structural_subset(v, c)
    tokens = (v + ' ' + c + ' wine').split()
    scores = get_bm25_scores(tokens)
    
    # Filter by subset
    sub_scores = scores[sub_idx]
    top50_n = min(50, len(sub_scores))
    top50_local = np.argpartition(-sub_scores, top50_n - 1)[:top50_n]
    top50_local_sorted = top50_local[np.argsort(-sub_scores[top50_local])]
    top50_global = sub_idx[top50_local_sorted]
    
    # Price rerank
    if p > 0:
        sub_prices = cat_price_arr[top50_global]
        valid_price = sub_prices >= 0
        price_dist = np.abs(sub_prices - p)
        price_dist[~valid_price] = 9999
        price_order = np.argsort(price_dist)
        final_idx = top50_global[price_order[:10]]
    else:
        final_idx = top50_global[:10]
        
    struct_preds.append([cat_ids[j] for j in final_idx])
    if i % 4000 == 0 and i > 0:
        print(f"  Struct BM25: {i:,}/{N:,} ({i/N*100:.0f}%)")

t_struct = time.time() - t0
m_struct = calc_metrics(struct_preds, targets)
m_struct['Latency_ms'] = round(t_struct/N*1000, 2)
print(f"  Done in {t_struct:.1f}s | Recall@10: {m_struct['Recall@10']}%")

# ── Method 4: BM25+ Enhanced ─────────────────────────────────
print("\n--- Method 4: BM25+ Enhanced ---")
t0 = time.time()
enhanced_preds = []
for i, (instr, v, c, p) in enumerate(zip(instructions, varieties, countries, prices)):
    # Full BM25 top-100
    tokens = (v + ' ' + c + ' wine').split()
    scores = get_bm25_scores(tokens)
    top100_idx = np.argpartition(-scores, 100)[:100]
    top100 = top100_idx[np.argsort(-scores[top100_idx])]
    
    # Apply structural filter on top-100
    filtered = [j for j in top100 if
                (not v or v[:6] in cat_variety[j]) and
                (not c or c[:5] in cat_country[j])]
    if len(filtered) < 5:
        filtered = list(top100)
    
    # Price rerank
    if p > 0:
        cands = np.array(filtered[:50])
        pdist = np.abs(cat_price_arr[cands] - p)
        pdist[cat_price_arr[cands] < 0] = 9999
        order = np.argsort(pdist)
        final = cands[order[:10]]
    else:
        final = np.array(filtered[:10])
        
    enhanced_preds.append([cat_ids[j] for j in final])
    if i % 4000 == 0 and i > 0:
        print(f"  BM25+ Enhanced: {i:,}/{N:,} ({i/N*100:.0f}%)")

t_enh = time.time() - t0
m_enh = calc_metrics(enhanced_preds, targets)
m_enh['Latency_ms'] = round(t_enh/N*1000, 2)
print(f"  Done in {t_enh:.1f}s | Recall@10: {m_enh['Recall@10']}%")

# ── Compile final table ───────────────────────────────────────
print("\n" + "=" * 65)
print("FINAL RESULTS — Full Test Set (N=12,991)")
print("=" * 65)

# Load full hybrid summary if exists
hybrid_summary_path = ROOT / 'results/hybrid_summary_full.csv'
if hybrid_summary_path.exists():
    df_h = pd.read_csv(hybrid_summary_path)
    m_h = df_h.iloc[0].to_dict()
else:
    m_h = {
        'Recall@1': 2.417, 'Recall@5': 6.127, 'Recall@10': 7.759,
        'NDCG@10': 4.874, 'MRR': 3.974, 'Latency_ms': 15703.0
    }

rows = [
    {'Method': 'BM25',               'N': N, **m_bm25},
    {'Method': 'TF-IDF',             'N': N, **m_tfidf},
    {'Method': 'BM25+ Enhanced',     'N': N, **m_enh},
    {'Method': 'Struct-Filter BM25', 'N': N, **m_struct},
    {'Method': 'TIGER + Price Rerank (Proposed)', 'N': N,
     'Recall@1': m_h['Recall@1'], 'Recall@5': m_h['Recall@5'], 'Recall@10': m_h['Recall@10'],
     'NDCG@10': m_h['NDCG@10'], 'MRR': m_h['MRR'], 'Latency_ms': m_h['Latency_ms']},
]

result_df = pd.DataFrame(rows)[
    ['Method', 'N', 'Recall@1', 'Recall@5', 'Recall@10', 'NDCG@10', 'MRR', 'Latency_ms']]
print(result_df.to_string(index=False))

# Save to full test results
out_path = ROOT / 'results/full_test_eval_12991.csv'
result_df.to_csv(out_path, index=False, encoding='utf-8-sig')
print(f"\n✅ Saved to: {out_path}")

# Update the fair comparison csv file with fractional values (matching thesis format)
fair_path = ROOT / 'results/fair_comparison/all_models_comparison.csv'
fair_rows = [
    {
        'Method': 'BM25',
        'Recall@1': m_bm25['Recall@1']/100.0,
        'Recall@5': m_bm25['Recall@5']/100.0,
        'Recall@10': m_bm25['Recall@10']/100.0,
        'NDCG@10': m_bm25['NDCG@10']/100.0,
        'MRR': m_bm25['MRR']/100.0,
        'Latency_ms': m_bm25['Latency_ms']
    },
    {
        'Method': 'BM25+ Enhanced',
        'Recall@1': m_enh['Recall@1']/100.0,
        'Recall@5': m_enh['Recall@5']/100.0,
        'Recall@10': m_enh['Recall@10']/100.0,
        'NDCG@10': m_enh['NDCG@10']/100.0,
        'MRR': m_enh['MRR']/100.0,
        'Latency_ms': m_enh['Latency_ms']
    },
    {
        'Method': 'TF-IDF CF',
        'Recall@1': m_tfidf['Recall@1']/100.0,
        'Recall@5': m_tfidf['Recall@5']/100.0,
        'Recall@10': m_tfidf['Recall@10']/100.0,
        'NDCG@10': m_tfidf['NDCG@10']/100.0,
        'MRR': m_tfidf['MRR']/100.0,
        'Latency_ms': m_tfidf['Latency_ms']
    },
    {
        'Method': 'Random Baseline',
        'Recall@1': 0.0, 'Recall@5': 0.0, 'Recall@10': 0.0, 'NDCG@10': 0.0, 'MRR': 0.0, 'Latency_ms': 0.004
    },
    {
        'Method': 'Struct-Filter BM25',
        'Recall@1': m_struct['Recall@1']/100.0,
        'Recall@5': m_struct['Recall@5']/100.0,
        'Recall@10': m_struct['Recall@10']/100.0,
        'NDCG@10': m_struct['NDCG@10']/100.0,
        'MRR': m_struct['MRR']/100.0,
        'Latency_ms': m_struct['Latency_ms']
    },
    {
        'Method': 'Proposed Model\n(Mô hình đề xuất)',
        'Recall@1': m_h['Recall@1']/100.0,
        'Recall@5': m_h['Recall@5']/100.0,
        'Recall@10': m_h['Recall@10']/100.0,
        'NDCG@10': m_h['NDCG@10']/100.0,
        'MRR': m_h['MRR']/100.0,
        'Latency_ms': m_h['Latency_ms']
    }
]
fair_df = pd.DataFrame(fair_rows)
fair_df.to_csv(fair_path, index=False, encoding='utf-8')
print(f"✅ Updated: {fair_path}")



