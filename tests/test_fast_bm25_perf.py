import sys, json, re, time
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import CountVectorizer

ROOT = Path(__file__).parents[1]
CATALOG_PATH = ROOT / 'data/processed/wine_catalog_semantic.csv'
TEST_PATH    = ROOT / 'data/processed/wine_test_130k.jsonl'

print("Loading catalog...")
cat = pd.read_csv(CATALOG_PATH,
    usecols=['title', 'variety', 'country', 'price', 'description',
             'Semantic_ID', 'doc_text'],
    dtype=str).fillna('')

print("Building CountVectorizer...")
t0 = time.time()
def dummy_tokenizer(text):
    return text.split()

vectorizer = CountVectorizer(tokenizer=dummy_tokenizer, lowercase=True)
tf_matrix = vectorizer.fit_transform(cat['doc_text']) # shape: (130k, vocab)
tf_matrix = tf_matrix.tocsc()
print(f"  CountVectorizer done in {time.time()-t0:.1f}s | shape: {tf_matrix.shape}")

N_docs = tf_matrix.shape[0]
doc_lens = np.array(tf_matrix.sum(axis=1)).flatten()
avgdl = doc_lens.mean()

# rank_bm25 IDF calculation
df = np.array((tf_matrix > 0).sum(axis=0)).flatten()
idf = np.log(N_docs - df + 0.5) - np.log(df + 0.5)
average_idf = idf.mean()
eps = 0.25 * average_idf
idf[idf < 0] = eps

vocab = vectorizer.vocabulary_
cat_ids = cat['Semantic_ID'].tolist()

# Prepare queries
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

queries = [f"{v} {c} wine" for v, c in zip(varieties, countries)]

# Parameters
k1 = 1.5
b = 0.75

# precompute doc_lens scaling
doc_len_factor = k1 * (1 - b + b * (doc_lens / avgdl))

# Test timing for first 500 queries with fully sparse calculations
print("Scoring first 500 queries (sparse ops)...")
t0 = time.time()
bm25_preds = []

for i, q in enumerate(queries[:500]):
    q_tokens = q.lower().split()
    scores = np.zeros(N_docs)
    for token in q_tokens:
        if token in vocab:
            idx = vocab[token]
            idf_val = idf[idx]
            
            # Get CSC column data directly
            # tf_matrix is in CSC format, so tf_matrix[:, idx] is extremely fast
            col = tf_matrix[:, idx]
            rows = col.indices
            tf_vals = col.data
            
            if len(rows) > 0:
                denom = tf_vals + doc_len_factor[rows]
                score_contrib = idf_val * tf_vals * (k1 + 1) / denom
                scores[rows] += score_contrib
    
    ranked = np.argsort(-scores)[:10]
    bm25_preds.append([cat_ids[j] for j in ranked])

t_elapsed = time.time() - t0
print(f"Scored 500 queries in {t_elapsed:.2f}s | Average {t_elapsed/500*1000:.1f}ms per query")
