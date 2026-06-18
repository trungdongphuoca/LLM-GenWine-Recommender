import math
import numpy as np
import pandas as pd
from scipy import sparse
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import CountVectorizer

corpus_texts = [
    "red wine from italy with cherry flavor",
    "white wine from france with citrus notes",
    "bold cabernet sauvignon from napa valley california",
    "sweet dessert wine from germany",
    "sparkling wine prosecco from italy",
]
queries = ["red wine italy", "sweet wine", "napa cabernet"]

# 1. rank_bm25
corpus_tokens = [text.split() for text in corpus_texts]
bm25 = BM25Okapi(corpus_tokens)

print("--- rank_bm25 scores ---")
for q in queries:
    print(f"Query: {q} -> {bm25.get_scores(q.split())}")

# 2. Vectorized sparse BM25
# Use a custom tokenizer to match rank_bm25's splitting behavior
def dummy_tokenizer(text):
    return text.split()

vectorizer = CountVectorizer(tokenizer=dummy_tokenizer, lowercase=True)
tf_matrix = vectorizer.fit_transform(corpus_texts)
feature_names = vectorizer.get_feature_names_out()
vocab = vectorizer.vocabulary_

N_docs = len(corpus_texts)
doc_lens = np.array(tf_matrix.sum(axis=1)).flatten()
avgdl = doc_lens.mean()

# Calculate df (document frequency) for each word in vocab
df = np.array((tf_matrix > 0).sum(axis=0)).flatten()

# Calculate rank_bm25 IDF exactly as in the inspect source code
idf = np.log(N_docs - df + 0.5) - np.log(df + 0.5)
# average idf
average_idf = idf.mean()
# floor negative idf
eps = 0.25 * average_idf
idf[idf < 0] = eps

# Parameters
k1 = 1.5
b = 0.75

def score_sparse_bm25(query_str):
    q_tokens = query_str.lower().split()
    scores = np.zeros(N_docs)
    for token in q_tokens:
        if token in vocab:
            idx = vocab[token]
            idf_val = idf[idx]
            # Get tf column for this term
            tf_col = tf_matrix[:, idx].toarray().flatten()
            # Calculate denominator: tf + k1 * (1 - b + b * (doc_lens / avgdl))
            denom = tf_col + k1 * (1 - b + b * (doc_lens / avgdl))
            # Calculate score contribution
            score_contrib = idf_val * tf_col * (k1 + 1) / denom
            scores += score_contrib
    return scores

print("\n--- Corrected Sparse BM25 scores ---")
for q in queries:
    print(f"Query: {q} -> {score_sparse_bm25(q)}")
