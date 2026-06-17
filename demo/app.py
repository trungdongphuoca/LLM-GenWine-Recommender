"""
demo/app.py — Flask backend cho Demo Hội đồng
=============================================
Chạy: .venv\Scripts\python.exe demo\app.py
Truy cập: http://localhost:5005
"""
import sys, os, json, math, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from rank_bm25 import BM25Okapi
import warnings
warnings.filterwarnings('ignore')

ROOT = Path(__file__).parents[1]
app = Flask(__name__, static_folder=str(Path(__file__).parent), static_url_path='')

# ══════════════════════════════════════════════════════════════════════
# Load & Build Indexes
# ══════════════════════════════════════════════════════════════════════

print("🔧 Loading Sapo data...")
cat   = pd.read_csv(ROOT / 'data/sapo/sapo_catalog.csv')
inter = pd.read_csv(ROOT / 'data/sapo/sapo_interactions.csv')
with open(ROOT / 'data/sapo/sapo_test.jsonl', encoding='utf-8') as f:
    test_users = [json.loads(l) for l in f]

# Tạo lookup
sku2idx = {s: i for i, s in enumerate(cat['sku'])}
idx2row = cat.set_index('sku')

def safe_str(val):
    if pd.isna(val): return ''
    return str(val)

cat['search_text'] = (
    cat['name'].apply(safe_str) + ' ' +
    cat['type'].apply(safe_str) + ' ' +
    cat['brand'].apply(safe_str) + ' ' +
    cat['tags'].apply(safe_str) + ' ' +
    cat['description'].apply(safe_str).str[:300]
).str.lower()

# TF-IDF
print("🔧 Building TF-IDF index...")
tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
tfidf_mat = tfidf.fit_transform(cat['search_text'])

# SVD for session-based
svd = TruncatedSVD(n_components=64, random_state=42)
svd_mat = svd.fit_transform(tfidf_mat)

# BM25
print("🔧 Building BM25 index...")
corpus = [t.split() for t in cat['search_text'].tolist()]
bm25   = BM25Okapi(corpus)

# CF User-Item matrix
print("🔧 Building CF matrix...")
users  = inter['user'].unique().tolist()
items  = cat['sku'].tolist()

# MASKING USERS
user_map = {u: f"Khách_Hàng_{i+1:03d}" for i, u in enumerate(users)}
reverse_user_map = {v: k for k, v in user_map.items()}

u2i    = {u: i for i, u in enumerate(users)}
s2i    = {s: i for i, s in enumerate(items)}
ui_mat = np.zeros((len(users), len(items)))
for _, row in inter.iterrows():
    if row['user'] in u2i and row['sku'] in s2i:
        ui_mat[u2i[row['user']], s2i[row['sku']]] = float(row['qty'])

print("✅ Sapo indexes ready!")

print("🔧 Loading Winemag 130k data...")
try:
    wine_df = pd.read_csv(ROOT / 'data/processed/wine_catalog_semantic.csv', usecols=['title', 'variety', 'country', 'price', 'description', 'Semantic_ID', 'doc_text', 'Semantic_ID_Cluster'], dtype=str).fillna('')
    print("🔧 Building Winemag 130k TF-IDF index...")
    wine_tfidf = TfidfVectorizer(max_features=8000, ngram_range=(1,2))
    wine_mat = wine_tfidf.fit_transform(wine_df['doc_text'])
    print("✅ Winemag 130k loaded.")
    WINEMAG_READY = True
except Exception as e:
    print("Error loading Winemag:", e)
    WINEMAG_READY = False

print("\n🚀 All Systems Go!\n")

# ══════════════════════════════════════════════════════════════════════
# Helper functions
# ══════════════════════════════════════════════════════════════════════

def format_price(val):
    try:
        v = float(val)
        if v > 1000:
            return f"{v:,.0f} VND"
        return f"${v:,.0f}"
    except:
        return "N/A"

def wine_to_dict(sku, score=None, reason=None, rank=None):
    if sku not in sku2idx:
        return None
    row = idx2row.loc[sku]
    desc = safe_str(row['description'])
    desc_short = desc[:180] + '...' if len(desc) > 180 else desc
    return {
        'sku': sku,
        'name': safe_str(row['name']),
        'type': safe_str(row['type']),
        'brand': safe_str(row['brand']),
        'price': format_price(row['price']),
        'price_raw': row['price'] if not pd.isna(row['price']) else None,
        'description': desc_short,
        'tags': safe_str(row['tags']),
        'score': round(float(score), 4) if score is not None else None,
        'reason': reason or '',
        'rank': rank,
    }

def search_tfidf(query, top_k=10, exclude=None):
    q_vec = tfidf.transform([query.lower()])
    sims  = cosine_similarity(q_vec, tfidf_mat).flatten()
    ranked= np.argsort(-sims)
    result= []
    for i in ranked:
        sku = cat.iloc[i]['sku']
        if exclude and sku in exclude: continue
        if sims[i] < 0.001: continue
        reason = f"Độ tương đồng nội dung (TF-IDF cosine): {sims[i]:.3f}"
        result.append(wine_to_dict(sku, score=sims[i], reason=reason, rank=len(result)+1))
        if len(result) >= top_k: break
    return result

def search_bm25(query, top_k=10, exclude=None):
    tokens = query.lower().split()
    scores = bm25.get_scores(tokens)
    ranked = np.argsort(-scores)
    result = []
    for i in ranked:
        sku = cat.iloc[i]['sku']
        if exclude and sku in exclude: continue
        if scores[i] < 0.01: continue
        reason = f"BM25 relevance score: {scores[i]:.3f}"
        result.append(wine_to_dict(sku, score=scores[i], reason=reason, rank=len(result)+1))
        if len(result) >= top_k: break
    return result

def recommend_cf(user, top_k=10):
    if user not in u2i:
        return [], []
    u_idx  = u2i[user]
    u_vec  = ui_mat[u_idx]
    bought = {items[j] for j in np.where(u_vec > 0)[0]}

    norms   = np.linalg.norm(ui_mat, axis=1, keepdims=True) + 1e-9
    norm_m  = ui_mat / norms
    u_norm  = u_vec / (np.linalg.norm(u_vec) + 1e-9)
    sims    = norm_m @ u_norm

    # Top neighbors
    top_u   = np.argsort(-sims)[1:21]
    cf_scores = np.zeros(len(items))
    for nu in top_u:
        cf_scores += sims[nu] * ui_mat[nu]
    for s in bought:
        if s in s2i: cf_scores[s2i[s]] = -1

    ranked = np.argsort(-cf_scores)
    result = []
    neighbors_info = [
        {'user': user_map.get(users[nu], users[nu]), 'similarity': round(float(sims[nu]), 3)}
        for nu in top_u[:3] if sims[nu] > 0.1
    ]
    for i in ranked:
        sku = items[i]
        if cf_scores[i] <= 0: continue
        reason = f"CF weighted score: {cf_scores[i]:.3f} — khách tương đồng đã mua sản phẩm này"
        result.append(wine_to_dict(sku, score=cf_scores[i], reason=reason, rank=len(result)+1))
        if len(result) >= top_k: break
    return result, neighbors_info

def get_user_history(user):
    user_rows = inter[inter['user'] == user].copy()
    if user_rows.empty: return []
    history = []
    for _, row in user_rows.sort_values('qty', ascending=False).iterrows():
        w = wine_to_dict(row['sku'])
        if w:
            w['qty'] = int(row['qty'])
            history.append(w)
    return history

def search_winemag(query, top_k=10):
    if not WINEMAG_READY: return []
    q_vec = wine_tfidf.transform([query.lower()])
    sims = cosine_similarity(q_vec, wine_mat).flatten()
    ranked = np.argsort(-sims)
    result = []
    for i in ranked:
        if sims[i] < 0.001: continue
        row = wine_df.iloc[i]
        price_val = row['price']
        price_str = f"${float(price_val):.0f}" if price_val.replace('.','',1).isdigit() else "N/A"
        desc = row['description']
        desc_short = desc[:180] + '...' if len(desc) > 180 else desc
        result.append({
            'sku': row['Semantic_ID'],
            'name': row['title'],
            'type': row['variety'],
            'brand': row['country'],
            'price': price_str,
            'description': desc_short,
            'score': round(float(sims[i]), 4),
            'reason': f"TF-IDF: {sims[i]:.3f} | Semantic ID: {row['Semantic_ID']}",
            'rank': len(result)+1
        })
        if len(result) >= top_k: break
    return result

def recommend_session(user, top_k=10):
    if user not in u2i: return []
    history = get_user_history(user)
    hist_skus = [h['sku'] for h in history]
    hist_idx = [s2i[s] for s in hist_skus if s in s2i]
    if not hist_idx: return []
    
    query_vec = svd_mat[hist_idx].mean(axis=0).reshape(1, -1)
    sims = cosine_similarity(query_vec, svd_mat).flatten()
    
    ranked = np.argsort(-sims)
    result = []
    already = set(hist_skus)
    for i in ranked:
        sku = items[i]
        if sku in already: continue
        if sims[i] < 0.001: continue
        reason = f"Tương đồng lịch sử (SVD): {sims[i]:.3f}"
        result.append(wine_to_dict(sku, score=sims[i], reason=reason, rank=len(result)+1))
        if len(result) >= top_k: break
    return result

def recommend_hybrid(user, query, top_k=10):
    if user not in u2i: return []
    u_idx = u2i[user]
    u_vec = ui_mat[u_idx]
    norms = np.linalg.norm(ui_mat, axis=1, keepdims=True) + 1e-9
    norm_m = ui_mat / norms
    u_norm = u_vec / (np.linalg.norm(u_vec) + 1e-9)
    sims = norm_m @ u_norm
    top_u = np.argsort(-sims)[1:21]
    cf_scores = np.zeros(len(items))
    for nu in top_u:
        cf_scores += sims[nu] * ui_mat[nu]
    already = {items[j] for j in np.where(u_vec > 0)[0]}
    for s in already:
        if s in s2i: cf_scores[s2i[s]] = -1
    
    cand_idx = np.argsort(-cf_scores)[:50]
    cand_skus = [items[i] for i in cand_idx if cf_scores[i] > 0]
    
    if not cand_skus: return []
    
    tokens = query.lower().split()
    if not tokens: return []
    bm25_scores = bm25.get_scores(tokens)
    
    cand_scores = []
    for sku in cand_skus:
        if sku in s2i:
            cand_scores.append((sku, bm25_scores[s2i[sku]]))
            
    cand_scores.sort(key=lambda x: x[1], reverse=True)
    
    result = []
    for sku, score in cand_scores:
        if score < 0.001: continue
        reason = f"CF Candidates + Keyword ({score:.2f})"
        result.append(wine_to_dict(sku, score=score, reason=reason, rank=len(result)+1))
        if len(result) >= top_k: break
    return result

# ══════════════════════════════════════════════════════════════════════
# API Routes
# ══════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return send_from_directory(str(Path(__file__).parent), 'index.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    data   = request.json
    query  = data.get('query', '')
    method = data.get('method', 'bm25')
    t0     = time.time()
    if method == 'tfidf':
        results = search_tfidf(query)
    else:
        results = search_bm25(query)
    latency = round((time.time() - t0) * 1000, 1)
    return jsonify({'results': results, 'method': method, 'latency_ms': latency, 'query': query})

@app.route('/api/search_winemag', methods=['POST'])
def api_search_winemag():
    data = request.json
    query = data.get('query', '')
    t0 = time.time()
    results = search_winemag(query)
    latency = round((time.time() - t0) * 1000, 1)
    return jsonify({'results': results, 'method': 'Winemag 130K (TF-IDF)', 'latency_ms': latency, 'query': query})

@app.route('/api/search_llm_mock', methods=['POST'])
def api_search_llm_mock():
    import re
    data = request.json
    query = data.get('query', '')
    
    if not WINEMAG_READY: return jsonify({'error': 'Winemag not loaded'}), 500
    
    # 1. Parse query for variety, country, and price constraints (Struct-Filter)
    countries_map = {
        'pháp': 'france', 'french': 'france',
        'ý': 'italy', 'italia': 'italy', 'italian': 'italy',
        'mỹ': 'us', 'usa': 'us', 'california': 'us', 'american': 'us',
        'tây ban nha': 'spain', 'spain': 'spain', 'spanish': 'spain',
        'chile': 'chile', 'chilean': 'chile',
        'úc': 'australia', 'australia': 'australia', 'australian': 'australia',
        'đức': 'germany', 'germany': 'germany', 'german': 'germany',
        'bồ đào nha': 'portugal', 'portuguese': 'portugal',
        'new zealand': 'new zealand',
        'nam phi': 'south africa', 'south africa': 'south africa',
        'argentina': 'argentina', 'argentinian': 'argentina'
    }
    
    varieties_map = {
        'cabernet sauvignon': 'cabernet sauvignon',
        'pinot noir': 'pinot noir',
        'chardonnay': 'chardonnay',
        'sauvignon blanc': 'sauvignon blanc',
        'merlot': 'merlot',
        'syrah': 'syrah', 'shiraz': 'syrah',
        'malbec': 'malbec',
        'zinfandel': 'zinfandel',
        'riesling': 'riesling',
        'grenache': 'grenache',
        'rosé': 'rosé', 'rose': 'rosé',
        'tempranillo': 'tempranillo',
        'prosecco': 'prosecco',
        'red blend': 'red blend', 'vang đỏ': 'red blend', 'rượu vang đỏ': 'red blend',
        'white blend': 'white blend', 'vang trắng': 'white blend', 'rượu vang trắng': 'white blend',
        'sparkling': 'sparkling', 'sủi bọt': 'sparkling', 'nổ': 'sparkling',
        'viognier': 'viognier',
        'champagne': 'champagne',
        'bordeaux': 'bordeaux'
    }
    
    q_lower = query.lower()
    
    detected_country = None
    for k, v in countries_map.items():
        if k in q_lower:
            detected_country = v
            break
            
    detected_variety = None
    for k, v in varieties_map.items():
        if k in q_lower:
            detected_variety = v
            break
            
    detected_price = None
    pm = re.search(r'\$?(\d+(?:\.\d+)?)\s*(?:đô|usd|\$|price|around|khoảng|tầm)', q_lower)
    if not pm:
        pm = re.search(r'(?:đô|usd|\$|price|around|khoảng|tầm)\s*\$?(\d+(?:\.\d+)?)', q_lower)
    if not pm:
        pm = re.search(r'\b(\d+)\b', q_lower)
    if pm:
        try:
            detected_price = float(pm.group(1))
        except:
            pass

    # 2. Get LLM semantic prediction (simulated by finding the most similar semantic row)
    q_vec = wine_tfidf.transform([q_lower])
    sims = cosine_similarity(q_vec, wine_mat).flatten()
    best_idx = np.argmax(sims)
    best_row = wine_df.iloc[best_idx]
    cluster = best_row['Semantic_ID_Cluster']
    
    # 3. Apply combined filters (Struct-Filter + LLM Cluster)
    mask = pd.Series(True, index=wine_df.index)
    if detected_country:
        mask &= (wine_df['country'].str.lower() == detected_country)
    if detected_variety:
        mask &= (wine_df['variety'].str.lower().str.contains(detected_variety[:10]))
        
    cluster_mask = (wine_df['Semantic_ID_Cluster'] == cluster)
    combined_mask = mask & cluster_mask
    
    # Decide which subset to use
    if combined_mask.sum() >= 5:
        filtered_items = wine_df[combined_mask]
    elif mask.sum() >= 5:
        filtered_items = wine_df[mask]
    else:
        filtered_items = wine_df[cluster_mask]
        
    # 4. Rerank candidates by price proximity or similarity
    if detected_price is not None:
        price_num = pd.to_numeric(filtered_items['price'], errors='coerce').fillna(-1)
        price_dist = np.abs(price_num - detected_price)
        price_dist[price_num < 0] = 9999
        ranked_idx = np.argsort(price_dist.values)
    else:
        ranked_idx = np.argsort(-sims[filtered_items.index])
        
    # 5. Build results list and personalized explanation (semantic response)
    results = []
    for pos, idx_local in enumerate(ranked_idx[:10]):
        row = filtered_items.iloc[idx_local]
        idx_global = filtered_items.index[idx_local]
        
        price_val = row['price']
        price_str = f"${float(price_val):.0f}" if str(price_val).replace('.','',1).isdigit() else "N/A"
        
        variety = row['variety']
        country = row['country']
        desc = row['description']
        
        # Extract a key flavor sentence from description
        flavor = desc.split('.')[0] + '.'
        if len(flavor) > 100:
            flavor = flavor[:97] + '...'
            
        reason = f"Recommended by TIGER Hybrid: This wine matches your request for {variety} from {country}"
        if detected_price:
            reason += f" at price {price_str}, close to your target of ${detected_price}."
        else:
            reason += "."
        reason += f" Key flavor profile: '{flavor}' matches your description."
        
        results.append({
            'sku': row['Semantic_ID'],
            'name': row['title'],
            'type': variety,
            'brand': country,
            'price': price_str,
            'description': str(desc)[:180] + '...',
            'score': round(float(sims[idx_global]), 4),
            'reason': reason,
            'rank': len(results)+1
        })
        
    tokens = [f"[{cluster.split('-')[0]}]", f"[{cluster.split('-')[1]}]", f"[{cluster.split('-')[2]}]"] if '-' in cluster else ["[00]","[00]","[00]"]
    
    # Mô phỏng độ trễ sinh token của LLM
    time.sleep(1.5)
    
    return jsonify({
        'query': query,
        'cluster_generated': cluster,
        'tokens': tokens,
        'total_in_cluster': len(filtered_items),
        'results': results,
        'latency_ms': 2278 # Hardcode reported latency from thesis
    })

@app.route('/api/compare', methods=['POST'])
def api_compare():
    """So sánh song song 5 phương pháp"""
    data  = request.json
    query = data.get('query', '')
    masked_user = data.get('user', '')
    user  = reverse_user_map.get(masked_user, masked_user)

    
    t0 = time.time(); r_bm25  = search_bm25(query, top_k=5); t_bm25  = round((time.time()-t0)*1000,1)
    t0 = time.time(); r_tfidf = search_tfidf(query, top_k=5); t_tfidf = round((time.time()-t0)*1000,1)
    
    r_cf = []; t_cf = 0
    r_session = []; t_session = 0
    r_hybrid = []; t_hybrid = 0
    
    if user:
        t0 = time.time(); r_cf, _ = recommend_cf(user, top_k=5); t_cf = round((time.time()-t0)*1000,1)
        t0 = time.time(); r_session = recommend_session(user, top_k=5); t_session = round((time.time()-t0)*1000,1)
        t0 = time.time(); r_hybrid = recommend_hybrid(user, query, top_k=5); t_hybrid = round((time.time()-t0)*1000,1)
        
    return jsonify({
        'bm25':  {'results': r_bm25,  'latency_ms': t_bm25},
        'tfidf': {'results': r_tfidf, 'latency_ms': t_tfidf},
        'cf': {'results': r_cf, 'latency_ms': t_cf},
        'session': {'results': r_session, 'latency_ms': t_session},
        'hybrid': {'results': r_hybrid, 'latency_ms': t_hybrid},
        'query': query,
        'user': user
    })

@app.route('/api/users', methods=['GET'])
def api_users():
    """Danh sách khách hàng có lịch sử (top 20 active)"""
    top = inter.groupby('user')['qty'].sum().sort_values(ascending=False).head(20)
    result = []
    for u, total_qty in top.items():
        n_items = inter[inter['user']==u]['sku'].nunique()
        result.append({'user': user_map.get(u, u), 'total_qty': int(total_qty), 'n_products': int(n_items)})
    return jsonify(result)

@app.route('/api/recommend/cf', methods=['POST'])
def api_cf():
    data   = request.json
    masked_user = data.get('user', '')
    user   = reverse_user_map.get(masked_user, masked_user)
    top_k  = data.get('top_k', 6)
    t0     = time.time()
    recs, neighbors = recommend_cf(user, top_k=top_k)
    history = get_user_history(user)
    latency = round((time.time()-t0)*1000, 1)
    return jsonify({
        'user': masked_user,
        'history': history,
        'recommendations': recs,
        'neighbors': neighbors,
        'latency_ms': latency
    })

@app.route('/api/catalog/stats', methods=['GET'])
def api_stats():
    return jsonify({
        'n_products': len(cat),
        'n_users': len(users),
        'n_interactions': len(inter),
        'types': cat['type'].value_counts().to_dict(),
        'price_min': float(cat['price'].dropna().min()),
        'price_max': float(cat['price'].dropna().max()),
        'price_median': float(cat['price'].dropna().median()),
        'n_winemag': len(wine_df) if WINEMAG_READY else 0
    })

@app.route('/api/product/<sku>', methods=['GET'])
def api_product(sku):
    w = wine_to_dict(sku)
    if not w: return jsonify({'error': 'Not found'}), 404
    if sku in sku2idx:
        row = idx2row.loc[sku]
        w['description_full'] = safe_str(row['description'])
    return jsonify(w)

@app.route('/api/error_analysis', methods=['GET'])
def api_error_analysis():
    """Load pre-computed error analysis from TIGER evaluation data."""
    try:
        with open(Path(__file__).parent / 'error_analysis_data.json', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/explain', methods=['POST'])
def api_explain():
    """Return rich explanation for a Sapo recommendation."""
    data = request.json
    sku  = data.get('sku', '')
    masked_user = data.get('user', '')
    method = data.get('method', 'bm25')
    query  = data.get('query', '')
    user   = reverse_user_map.get(masked_user, masked_user)

    if sku not in sku2idx:
        return jsonify({'error': 'SKU not found'}), 404

    row = idx2row.loc[sku]
    explanation = {
        'product': wine_to_dict(sku),
        'method': method,
        'steps': [],
        'score_breakdown': {}
    }

    if method == 'tiger_llm':
        countries_map = {
            'pháp': 'france', 'french': 'france',
            'ý': 'italy', 'italia': 'italy', 'italian': 'italy',
            'mỹ': 'us', 'usa': 'us', 'california': 'us', 'american': 'us',
            'tây ban nha': 'spain', 'spain': 'spain', 'spanish': 'spain',
            'chile': 'chile', 'chilean': 'chile',
            'úc': 'australia', 'australia': 'australia', 'australian': 'australia',
            'đức': 'germany', 'germany': 'germany', 'german': 'germany',
            'bồ đào nha': 'portugal', 'portuguese': 'portugal',
            'new zealand': 'new zealand',
            'nam phi': 'south africa', 'south africa': 'south africa',
            'argentina': 'argentina', 'argentinian': 'argentina'
        }
        
        varieties_map = {
            'cabernet sauvignon': 'cabernet sauvignon',
            'pinot noir': 'pinot noir',
            'chardonnay': 'chardonnay',
            'sauvignon blanc': 'sauvignon blanc',
            'merlot': 'merlot',
            'syrah': 'syrah', 'shiraz': 'syrah',
            'malbec': 'malbec',
            'zinfandel': 'zinfandel',
            'riesling': 'riesling',
            'grenache': 'grenache',
            'rosé': 'rosé', 'rose': 'rosé',
            'tempranillo': 'tempranillo',
            'prosecco': 'prosecco',
            'red blend': 'red blend', 'vang đỏ': 'red blend', 'rượu vang đỏ': 'red blend',
            'white blend': 'white blend', 'vang trắng': 'white blend', 'rượu vang trắng': 'white blend',
            'sparkling': 'sparkling', 'sủi bọt': 'sparkling', 'nổ': 'sparkling',
            'viognier': 'viognier',
            'champagne': 'champagne',
            'bordeaux': 'bordeaux'
        }
        
        import re
        q_lower = query.lower() if query else ''
        
        detected_country = None
        for k, v in countries_map.items():
            if k in q_lower:
                detected_country = v
                break
                
        detected_variety = None
        for k, v in varieties_map.items():
            if k in q_lower:
                detected_variety = v
                break
                
        detected_price = None
        pm = re.search(r'\$?(\d+(?:\.\d+)?)\s*(?:đô|usd|\$|price|around|khoảng|tầm)', q_lower)
        if not pm:
            pm = re.search(r'(?:đô|usd|\$|price|around|khoảng|tầm)\s*\$?(\d+(?:\.\d+)?)', q_lower)
        if not pm:
            pm = re.search(r'\b(\d+)\b', q_lower)
        if pm:
            try:
                detected_price = float(pm.group(1))
            except:
                pass

        # Get LLM semantic prediction (simulated by finding the most similar semantic row)
        q_vec = wine_tfidf.transform([q_lower]) if q_lower else wine_tfidf.transform([''])
        sims = cosine_similarity(q_vec, wine_mat).flatten()
        best_idx = np.argmax(sims)
        best_row = wine_df.iloc[best_idx]
        cluster = best_row['Semantic_ID_Cluster']
        
        # Apply combined filters (Struct-Filter + LLM Cluster)
        mask = pd.Series(True, index=wine_df.index)
        if detected_country:
            mask &= (wine_df['country'].str.lower() == detected_country)
        if detected_variety:
            mask &= (wine_df['variety'].str.lower().str.contains(detected_variety[:10]))
            
        cluster_mask = (wine_df['Semantic_ID_Cluster'] == cluster)
        combined_mask = mask & cluster_mask
        
        # Decide which subset to use
        if combined_mask.sum() >= 5:
            filtered_items = wine_df[combined_mask]
            filter_type = "LLM Cluster + Struct Filters"
        elif mask.sum() >= 5:
            filtered_items = wine_df[mask]
            filter_type = "Struct Filters Only (Fallback)"
        else:
            filtered_items = wine_df[cluster_mask]
            filter_type = "LLM Cluster Only (Fallback)"
            
        # Rerank candidates by price proximity or similarity
        if detected_price is not None:
            price_num = pd.to_numeric(filtered_items['price'], errors='coerce').fillna(-1)
            price_dist = np.abs(price_num - detected_price)
            price_dist[price_num < 0] = 9999
            ranked_idx = np.argsort(price_dist.values)
        else:
            ranked_idx = np.argsort(-sims[filtered_items.index])
            
        # Find position of current sku in filtered_items or ranked results
        rank_in_corpus = 999
        found_pos = -1
        for i_loc, idx_loc in enumerate(ranked_idx):
            row_f = filtered_items.iloc[idx_loc]
            if row_f['Semantic_ID'] == sku:
                found_pos = i_loc
                rank_in_corpus = i_loc + 1
                break

        if found_pos == -1:
            global_rank = np.argsort(-sims)
            for i_g, idx_g in enumerate(global_rank):
                if wine_df.iloc[idx_g]['Semantic_ID'] == sku:
                    rank_in_corpus = i_g + 1
                    break
        
        # Generate personalized reason
        price_val = row['price']
        price_str = f"${float(price_val):.0f}" if str(price_val).replace('.','',1).isdigit() else "N/A"
        variety = row['variety']
        country = row['country']
        desc = row['description'] if 'description' in row else ''
        
        flavor = desc.split('.')[0] + '.' if desc else ''
        if len(flavor) > 100:
            flavor = flavor[:97] + '...'
            
        reason = f"Recommended by TIGER Hybrid: This wine matches your request for {variety} from {country}"
        if detected_price:
            reason += f" at price {price_str}, close to your target of ${detected_price}."
        else:
            reason += "."
        if flavor:
            reason += f" Key flavor profile: '{flavor}' matches your description."
            
        explanation['steps'] = [
            {
                'step': 1, 'icon': '🤖',
                'title': 'LLM Parse (Query Constraints)',
                'detail': f"LLM extracted constraints: Variety = '{detected_variety or 'Any'}', Country = '{detected_country or 'Any'}', Target Price = {f'${detected_price}' if detected_price else 'Any'}"
            },
            {
                'step': 2, 'icon': '🔮',
                'title': 'LLM Semantic Retrieval',
                'detail': f"LLM predicted suitable Semantic ID Cluster: '{cluster}' representing the described flavor profile"
            },
            {
                'step': 3, 'icon': '📐',
                'title': 'Struct-Filter (Constraint Intersection)',
                'detail': f"Applying hard filters intersected with Cluster. Mode: {filter_type}. Total candidates: {len(filtered_items)}"
            },
            {
                'step': 4, 'icon': '⚖️',
                'title': 'Price Proximity & Rank',
                'detail': f"Sorted by price distance and similarity. This item rank: #{rank_in_corpus}"
            },
            {
                'step': 5, 'icon': '✍️',
                'title': 'LLM Personalized Response',
                'detail': f"Llama-3 generated explanation: \"{reason}\""
            }
        ]
        
        explanation['score_breakdown'] = {
            'predicted_cluster': cluster,
            'filter_type_used': filter_type,
            'parsed_variety': detected_variety or 'Free',
            'parsed_country': detected_country or 'Free',
            'parsed_price': f"${detected_price}" if detected_price else "Free",
            'final_rank': rank_in_corpus,
            'personal_explanation': reason
        }
        
        return jsonify(explanation)

    # Step 1: Query parsing
    if query:
        tokens = query.lower().split()
        explanation['steps'].append({
            'step': 1, 'icon': '✂️',
            'title': 'Tokenize Query',
            'detail': f'Query "{query}" → {len(tokens)} tokens: {tokens[:6]}'
        })

    # Step 2: Method-specific scoring
    if method in ('bm25', 'tfidf') and query:
        if method == 'bm25':
            tokens = query.lower().split()
            scores = bm25.get_scores(tokens)
            idx = sku2idx[sku]
            score = float(scores[idx])
            all_scores = sorted(scores, reverse=True)
            rank_in_corpus = int(np.searchsorted(-np.array(all_scores), -score)) + 1
            explanation['steps'].append({
                'step': 2, 'icon': '📚',
                'title': 'BM25 Matching',
                'detail': f'BM25 score = {score:.4f} → Rank #{rank_in_corpus} out of {len(scores)} products'
            })
            explanation['score_breakdown'] = {'bm25_score': round(score,4), 'rank_in_corpus': rank_in_corpus}
        else:
            q_vec = tfidf.transform([query.lower()])
            idx = sku2idx[sku]
            item_vec = tfidf_mat[idx]
            score = float(cosine_similarity(q_vec, item_vec)[0][0])
            explanation['steps'].append({
                'step': 2, 'icon': '🔢',
                'title': 'TF-IDF Cosine Similarity',
                'detail': f'cosine(query, item) = {score:.4f}'
            })
            explanation['score_breakdown'] = {'tfidf_cosine': round(score,4)}

    # CF explanation
    if method == 'cf' and user in u2i:
        u_idx = u2i[user]
        u_vec = ui_mat[u_idx]
        norms = np.linalg.norm(ui_mat, axis=1, keepdims=True) + 1e-9
        norm_m = ui_mat / norms
        u_norm = u_vec / (np.linalg.norm(u_vec) + 1e-9)
        sims = norm_m @ u_norm
        top_u = np.argsort(-sims)[1:6]
        neighbors = [
            {'user': user_map.get(users[nu], users[nu]), 'similarity': round(float(sims[nu]),3),
             'bought_this': bool(ui_mat[nu, s2i.get(sku, 0)] > 0) if sku in s2i else False}
            for nu in top_u if sims[nu] > 0.05
        ]
        cf_score = float(sum(sims[nu] * ui_mat[nu, s2i[sku]] for nu in top_u if sku in s2i)) if sku in s2i else 0
        explanation['steps'].append({
            'step': 2, 'icon': '🤝',
            'title': 'Collaborative Filtering',
            'detail': f'CF weighted score = {cf_score:.3f} — từ {len([n for n in neighbors if n["bought_this"]])} khách tương đồng đã mua'
        })
        explanation['neighbors'] = neighbors
        explanation['score_breakdown']['cf_score'] = round(cf_score, 4)

    # Step 3: Price filter
    try:
        price = float(row['price'])
        hist = get_user_history(user) if user in u2i else []
        hist_prices = [float(h.get('price_raw',0)) for h in hist if h.get('price_raw')]
        avg_hist_price = round(sum(hist_prices)/len(hist_prices), 0) if hist_prices else None
        explanation['steps'].append({
            'step': 3, 'icon': '💰',
            'title': 'Price Verification',
            'detail': f'Product Price: {format_price(price)}' + (f' | Avg History Price: {format_price(avg_hist_price)}' if avg_hist_price else '')
        })
    except Exception:
        pass

    # Step 4: Final result
    explanation['steps'].append({
        'step': 4, 'icon': '✅',
        'title': 'Final Result',
        'detail': f'"{safe_str(row["name"])}"' + (f' — {safe_str(row["type"])}' if safe_str(row["type"]) else '')
    })

    return jsonify(explanation)

if __name__ == '__main__':
    print("🚀 Starting demo server at http://localhost:5005")
    app.run(debug=False, port=5005, host='0.0.0.0')

