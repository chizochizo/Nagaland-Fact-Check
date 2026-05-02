from retrieval.bm25_retrieval import search_bm25
from retrieval.dense_retrieval import search_dense


def reciprocal_rank_fusion(bm25_results, dense_results, k=60):
    """
    Combines results from BM25 and Dense using RRF.
    """
    scores = {}

    # 1. BM25
    for rank, (score, text) in enumerate(bm25_results):
        if text not in scores:
            scores[text] = 0
        scores[text] += 1 / (k + rank + 1)

    # 2. Dense
    for rank, (score, text) in enumerate(dense_results):
        if text not in scores:
            scores[text] = 0
        scores[text] += 1 / (k + rank + 1)

    # 3. Sort
    sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # ✅ FIXED FORMAT: (score, text)
    return [(score, text) for text, score in sorted_results]


def search_hybrid(query, top_k=3):
    """
    The main entry point for the Hybrid Search.
    """
    bm25_res = search_bm25(query, top_k=10)
    dense_res = search_dense(query, top_k=10)

    fused_results = reciprocal_rank_fusion(bm25_res, dense_res)

    return fused_results[:top_k]
