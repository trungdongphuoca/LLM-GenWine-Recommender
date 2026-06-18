import time
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).parents[1]
CATALOG_PATH = ROOT / 'data/processed/wine_catalog_semantic.csv'

print("Loading catalog...")
cat = pd.read_csv(CATALOG_PATH, usecols=['doc_text'], dtype=str).fillna('')

print("Building TfidfVectorizer...")
t0 = time.time()
tfidf = TfidfVectorizer(max_features=10000, ngram_range=(1, 2), min_df=2)
tfidf_mat = tfidf.fit_transform(cat['doc_text']) # shape: (130k, vocab)
print(f"TfidfVectorizer done in {time.time()-t0:.2f}s")

# Create a batch of queries
queries = ["red wine from italy", "sweet white wine from germany", "bold cabernet from napa california"] * 100
print(f"Created {len(queries)} queries")

t0 = time.time()
Q_tfidf = tfidf.transform(queries)
print(f"Query transform took {time.time()-t0:.4f}s")

# 1. Cosine similarity
t0 = time.time()
sims1 = cosine_similarity(Q_tfidf, tfidf_mat)
print(f"cosine_similarity took {time.time()-t0:.4f}s")

# 2. Sparse dot product
t0 = time.time()
# tfidf_mat and Q_tfidf are already L2 normalized by TfidfVectorizer
sims2 = Q_tfidf.dot(tfidf_mat.T).toarray()
print(f"Sparse dot product took {time.time()-t0:.4f}s")

# Compare values
print(f"Max difference: {np.abs(sims1 - sims2).max():.2e}")
