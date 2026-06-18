from rank_bm25 import BM25Okapi

corpus_texts = [
    "red wine from italy with cherry flavor",
    "white wine from france with citrus notes",
    "bold cabernet sauvignon from napa valley california",
    "sweet dessert wine from germany",
    "sparkling wine prosecco from italy",
]
corpus_tokens = [text.split() for text in corpus_texts]
bm25 = BM25Okapi(corpus_tokens)

print("bm25.doc_len:", bm25.doc_len)
print("bm25.avgdl:", bm25.avgdl)
print("bm25.corpus_size:", bm25.corpus_size)
for q in ["red", "wine", "italy"]:
    print(f"Token: {q}")
    print(f"  IDF in rank_bm25: {bm25.idf.get(q, 0)}")
    print(f"  doc_freqs: {[d.get(q, 0) for d in bm25.doc_freqs]}")
