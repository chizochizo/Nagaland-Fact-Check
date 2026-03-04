import math
from collections import Counter, defaultdict


class BM25Retriever:
    def __init__(self, documents, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.documents = documents
        self.N = len(documents)

        self.doc_len = []
        self.avg_doc_len = 0
        self.term_freqs = []
        self.doc_freqs = defaultdict(int)
        self.idf = {}

        self._initialize()

    def _tokenize(self, text):
        return text.lower().split()

    def _initialize(self):
        total_len = 0

        for doc in self.documents:
            tokens = self._tokenize(doc)
            total_len += len(tokens)

            freq = Counter(tokens)
            self.term_freqs.append(freq)
            self.doc_len.append(len(tokens))

            for term in freq:
                self.doc_freqs[term] += 1

        self.avg_doc_len = total_len / self.N if self.N > 0 else 0

        for term, df in self.doc_freqs.items():
            self.idf[term] = math.log(1 + (self.N - df + 0.5) / (df + 0.5))

    def search(self, query, top_k=3):
        query_tokens = self._tokenize(query)
        scores = []

        for idx, doc in enumerate(self.documents):
            score = 0
            doc_len = self.doc_len[idx]
            freq = self.term_freqs[idx]

            for term in query_tokens:
                if term not in freq:
                    continue

                idf = self.idf.get(term, 0)
                tf = freq[term]

                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (
                    1 - self.b + self.b * (doc_len / self.avg_doc_len)
                )

                score += idf * (numerator / denominator)

            scores.append((score, doc))

        scores.sort(reverse=True, key=lambda x: x[0])
        return scores[:top_k]
