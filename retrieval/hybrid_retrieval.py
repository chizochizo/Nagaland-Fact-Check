from retrieval.bm25_retrieval import search_bm25
from retrieval.dense_retrieval import search_dense


def reciprocal_rank_fusion(bm25_results, dense_results, k=60):
    """
    Combines results from BM25 and Dense using RRF.
    k is a constant that controls how much weight to give to lower-ranked items.
    """
    scores = {}  # Map of {doc_text: combined_score}

    # 1. Process BM25 Results
    for rank, (score, text) in enumerate(bm25_results):
        if text not in scores:
            scores[text] = 0
        scores[text] += 1 / (k + rank + 1)

    # 2. Process Dense Results
    for rank, (score, text) in enumerate(dense_results):
        if text not in scores:
            scores[text] = 0
        scores[text] += 1 / (k + rank + 1)

    # 3. Sort by combined score
    sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_results


def search_hybrid(query, top_k=3):
    """
    The main entry point for the Hybrid Search.
    """
    # Get top 10 from each to have a good pool for fusion
    bm25_res = search_bm25(query, top_k=10)
    dense_res = search_dense(query, top_k=10)

    # Merge them
    fused_results = reciprocal_rank_fusion(bm25_res, dense_res)

    # Return in the standard (score, text) format
    return fused_results[:top_k]
