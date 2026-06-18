"""
sapo/sapo_ablation.py
=====================
Ablation Study trên dữ liệu Sapo thực tế Việt Nam.

So sánh 5 phương pháp:
  M1 - Content-Based TF-IDF (không dùng user history)
  M2 - Content-Based BM25   (không dùng user history)
  M3 - Collaborative Filtering (User-Item cosine)
  M4 - Session-Based (Last-K items similarity)
  M5 - Hybrid: CF + Content rerank (best of both worlds)

Evaluation: Leave-One-Out trên 202 eligible users
Metrics: Recall@1, Recall@5, Recall@10, NDCG@10, MRR
"""
import sys, os, json, math, re
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parents[1]))
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import warnings
warnings.filterwarnings('ignore')

ROOT = Path(__file__).parents[1]
DATA = ROOT / 'data' / 'sapo'

# ── Metrics ──────────────────────────────────────────────────────────────
def recall_k(target, ranked, k):
    return 1.0 if target in ranked[:k] else 0.0

def ndcg_10(target, ranked):
    for i, x in enumerate(ranked[:10]):
        if x == target:
            return 1.0 / math.log2(i + 2)
    return 0.0

def mrr(target, ranked):
    for i, x in enumerate(ranked[:10]):
        if x == target:
            return 1.0 / (i + 1)
    return 0.0

def compute_metrics(results):
    df = pd.DataFrame(results)
    return {
        'Recall@1':  df['r1'].mean()    * 100,
        'Recall@5':  df['r5'].mean()    * 100,
        'Recall@10': df['r10'].mean()   * 100,
        'NDCG@10':   df['ndcg'].mean()  * 100,
        'MRR':       df['mrr'].mean()   * 100,
    }

def eval_method(name, get_ranked_fn, test_records, cat):
    results = []
    for rec in test_records:
        ranked = get_ranked_fn(rec, cat)
        target = rec['target_sku']
        results.append({
            'r1':   recall_k(target, ranked, 1),
            'r5':   recall_k(target, ranked, 5),
            'r10':  recall_k(target, ranked, 10),
            'ndcg': ndcg_10(target, ranked),
            'mrr':  mrr(target, ranked),
        })
    metrics = compute_metrics(results)
    metrics['Method'] = name
    return metrics

# ── Load data ────────────────────────────────────────────────────────────
def load_data():
    cat   = pd.read_csv(DATA / 'sapo_catalog.csv')
    inter = pd.read_csv(DATA / 'sapo_interactions.csv')
    test  = []
    with open(DATA / 'sapo_test.jsonl', encoding='utf-8') as f:
        for line in f:
            test.append(json.loads(line))
    return cat, inter, test

# ── Build TF-IDF index ───────────────────────────────────────────────────
def build_tfidf(cat):
    texts = cat['full_text'].fillna('').tolist()
    tfidf = TfidfVectorizer(max_features=8000, ngram_range=(1,2))
    mat   = tfidf.fit_transform(texts)
    return tfidf, mat

# ── M1: Content-Based TF-IDF ────────────────────────────────────────────
def m1_content_tfidf(rec, cat, tfidf, mat):
    query = rec['instruction']
    # Dùng tên SP trong history làm query
    hist_names = ', '.join([
        cat[cat['sku'] == s]['name'].values[0]
        for s in rec['history_skus']
        if not cat[cat['sku'] == s].empty
    ])
    q_vec = tfidf.transform([hist_names if hist_names else query])
    sims  = cosine_similarity(q_vec, mat).flatten()
    ranked_idx = np.argsort(-sims)
    ranked = [cat.iloc[i]['sku'] for i in ranked_idx]
    return ranked[:10]

# ── M2: BM25 Content ─────────────────────────────────────────────────────
def build_bm25(cat):
    try:
        from rank_bm25 import BM25Okapi
        corpus = [t.lower().split() for t in cat['full_text'].fillna('').tolist()]
        bm25   = BM25Okapi(corpus)
        return bm25
    except ImportError:
        return None

def m2_bm25(rec, cat, bm25):
    if bm25 is None:
        return []
    hist_names = ' '.join([
        cat[cat['sku'] == s]['name'].values[0]
        for s in rec['history_skus']
        if not cat[cat['sku'] == s].empty
    ])
    query_tokens = hist_names.lower().split() if hist_names else rec['instruction'].lower().split()
    scores  = bm25.get_scores(query_tokens)
    ranked_idx = np.argsort(-scores)
    return [cat.iloc[i]['sku'] for i in ranked_idx[:10]]

# ── M3: Collaborative Filtering ──────────────────────────────────────────
def build_user_item(cat, inter):
    users = inter['user'].unique().tolist()
    items = cat['sku'].tolist()
    u2i   = {u: i for i, u in enumerate(users)}
    s2i   = {s: i for i, s in enumerate(items)}

    mat = np.zeros((len(users), len(items)))
    for _, row in inter.iterrows():
        if row['user'] in u2i and row['sku'] in s2i:
            mat[u2i[row['user']], s2i[row['sku']]] = row['qty']
    return mat, users, items, u2i, s2i

def m3_cf(rec, cat, ui_mat, users, items, u2i, s2i):
    user = rec['user']
    if user not in u2i:
        return []

    u_idx  = u2i[user]
    u_vec  = ui_mat[u_idx]

    # Loại bỏ items đã mua
    already = set(rec['history_skus'])

    # Tìm users tương đồng (cosine)
    norms  = np.linalg.norm(ui_mat, axis=1, keepdims=True) + 1e-9
    norm_mat = ui_mat / norms
    u_norm = u_vec / (np.linalg.norm(u_vec) + 1e-9)
    sims   = norm_mat @ u_norm

    # Weighted sum of neighbor purchases
    top_users = np.argsort(-sims)[1:21]  # top 20 neighbors
    scores    = np.zeros(len(items))
    for nu in top_users:
        scores += sims[nu] * ui_mat[nu]

    # Zero out already-bought
    for s in already:
        if s in s2i:
            scores[s2i[s]] = -1

    ranked_idx = np.argsort(-scores)
    return [items[i] for i in ranked_idx[:10]]

# ── M4: Session-Based (Last-K similarity) ────────────────────────────────
def m4_session(rec, cat, mat, svd_mat):
    """
    Dùng embedding trung bình của history items để tìm similar items
    """
    hist_skus = rec['history_skus']
    hist_idx  = [
        cat[cat['sku'] == s].index[0]
        for s in hist_skus
        if not cat[cat['sku'] == s].empty
    ]
    if not hist_idx:
        return []

    # Mean embedding của history
    hist_vecs = svd_mat[hist_idx]
    query_vec = hist_vecs.mean(axis=0).reshape(1, -1)

    sims      = cosine_similarity(query_vec, svd_mat).flatten()
    already   = set(hist_skus)

    sorted_idx = np.argsort(-sims)
    ranked = []
    for i in sorted_idx:
        sku = cat.iloc[i]['sku']
        if sku not in already:
            ranked.append(sku)
        if len(ranked) >= 10:
            break
    return ranked

# ── M5: Hybrid CF + Content ──────────────────────────────────────────────
def m5_hybrid(rec, cat, ui_mat, users, items, u2i, s2i, svd_mat):
    """
    Lấy CF candidates → re-rank bằng content similarity
    """
    # CF candidates (top 50)
    user = rec['user']
    already = set(rec['history_skus'])

    if user in u2i:
        u_idx   = u2i[user]
        u_vec   = ui_mat[u_idx]
        norms   = np.linalg.norm(ui_mat, axis=1, keepdims=True) + 1e-9
        norm_mat= ui_mat / norms
        u_norm  = u_vec / (np.linalg.norm(u_vec) + 1e-9)
        sims    = norm_mat @ u_norm
        top_u   = np.argsort(-sims)[1:21]
        cf_scores = np.zeros(len(items))
        for nu in top_u:
            cf_scores += sims[nu] * ui_mat[nu]
        for s in already:
            if s in s2i:
                cf_scores[s2i[s]] = -1
        cf_cands = [items[i] for i in np.argsort(-cf_scores)[:50]]
    else:
        cf_cands = cat['sku'].tolist()[:50]

    # Content re-rank using history embedding
    hist_idx = [
        cat[cat['sku'] == s].index[0]
        for s in rec['history_skus']
        if not cat[cat['sku'] == s].empty
    ]
    if hist_idx:
        query_vec = svd_mat[hist_idx].mean(axis=0).reshape(1, -1)
        cand_idx  = [
            cat[cat['sku'] == s].index[0]
            for s in cf_cands
            if not cat[cat['sku'] == s].empty
        ]
        if cand_idx:
            cand_vecs = svd_mat[cand_idx]
            sims_c    = cosine_similarity(query_vec, cand_vecs).flatten()
            reranked  = [cf_cands[i] for i in np.argsort(-sims_c)]
            return reranked[:10]

    return cf_cands[:10]

# ── Main ──────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Sapo Ablation Study — 5 Methods")
    print("=" * 60)

    cat, inter, test = load_data()
    print(f"  Catalog: {len(cat)} products")
    print(f"  Test users: {len(test)}")

    print("\nBuilding indexes...")
    tfidf, tfidf_mat = build_tfidf(cat)

    # SVD embeddings for session-based
    svd   = TruncatedSVD(n_components=64, random_state=42)
    svd_mat = svd.fit_transform(tfidf_mat)

    bm25 = build_bm25(cat)
    ui_mat, users, items, u2i, s2i = build_user_item(cat, inter)

    all_results = []

    print("\nEvaluating methods...")

    # M1: Content TF-IDF
    print("  M1: Content-Based TF-IDF...")
    r = eval_method(
        "M1: Content TF-IDF (no history)",
        lambda rec, cat: m1_content_tfidf(rec, cat, tfidf, tfidf_mat),
        test, cat
    )
    all_results.append(r)
    print(f"    R@1={r['Recall@1']:.2f}%  R@10={r['Recall@10']:.2f}%  NDCG@10={r['NDCG@10']:.2f}%")

    # M2: Bm25
    print("  M2: Content BM25...")
    r = eval_method(
        "M2: Content BM25 (no history)",
        lambda rec, cat: m2_bm25(rec, cat, bm25),
        test, cat
    )
    all_results.append(r)
    print(f"    R@1={r['Recall@1']:.2f}%  R@10={r['Recall@10']:.2f}%  NDCG@10={r['NDCG@10']:.2f}%")

    # M3: Cf
    print("  M3: Collaborative Filtering...")
    r = eval_method(
        "M3: Collaborative Filtering",
        lambda rec, cat: m3_cf(rec, cat, ui_mat, users, items, u2i, s2i),
        test, cat
    )
    all_results.append(r)
    print(f"    R@1={r['Recall@1']:.2f}%  R@10={r['Recall@10']:.2f}%  NDCG@10={r['NDCG@10']:.2f}%")

    # M4: Session-Based
    print("  M4: Session-Based (history embedding)...")
    r = eval_method(
        "M4: Session-Based (purchase history)",
        lambda rec, cat: m4_session(rec, cat, tfidf_mat, svd_mat),
        test, cat
    )
    all_results.append(r)
    print(f"    R@1={r['Recall@1']:.2f}%  R@10={r['Recall@10']:.2f}%  NDCG@10={r['NDCG@10']:.2f}%")

    # M5: Hybrid
    print("  M5: Hybrid CF + Content Rerank...")
    r = eval_method(
        "M5: Hybrid CF + Content (Ours)",
        lambda rec, cat: m5_hybrid(rec, cat, ui_mat, users, items, u2i, s2i, svd_mat),
        test, cat
    )
    all_results.append(r)
    print(f"    R@1={r['Recall@1']:.2f}%  R@10={r['Recall@10']:.2f}%  NDCG@10={r['NDCG@10']:.2f}%")

    # ── Summary ───────────────────────────────────────────────────────
    print("\n=== SAPO ABLATION RESULTS ===")
    df_out = pd.DataFrame(all_results)[['Method','Recall@1','Recall@5','Recall@10','NDCG@10','MRR']]
    print(df_out.to_string(index=False))

    out_path = ROOT / 'results' / 'sapo_ablation_results.csv'
    df_out.to_csv(out_path, index=False)
    print(f"\nSaved: {out_path}")
    return df_out

if __name__ == '__main__':
    main()
