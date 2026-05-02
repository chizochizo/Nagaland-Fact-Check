from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

class CrossReranker:
    def __init__(self):
        print("🔄 Loading Cross-Encoder...")
        self.model = CrossEncoder(MODEL_NAME)

    def rerank(self, query, documents, top_k=7):
        """
        documents: list of (score, text)
        returns: re-ranked list (score, text)
        """

        if not documents:
            return []

        texts = [text for _, text in documents]

        pairs = [(query, text) for text in texts]

        ce_scores = self.model.predict(pairs)

        reranked = []

        for i, (orig_score, text) in enumerate(documents):
            try:
                orig_score = float(orig_score)
            except:
                orig_score = 0.5

            ce_score = float(ce_scores[i])

            # 🔥 FINAL SCORE = COMBINATION (IMPORTANT)
            final_score = (0.6 * ce_score) + (0.4 * orig_score)

            reranked.append((final_score, text))

        # Sort by final combined score
        reranked.sort(key=lambda x: x[0], reverse=True)

        return reranked[:top_k]


# Singleton
_reranker = None

def rerank_results(query, docs, top_k=7):
    global _reranker
    if _reranker is None:
        _reranker = CrossReranker()

    return _reranker.rerank(query, docs, top_k)