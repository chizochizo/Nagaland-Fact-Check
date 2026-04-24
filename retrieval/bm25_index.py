import math
import os
import json
from collections import Counter, defaultdict

# --- 1. THE ENGINE (Class) ---


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
        if self.N == 0:
            return
        total_len = 0
        for doc in self.documents:
            tokens = self._tokenize(doc)
            total_len += len(tokens)
            freq = Counter(tokens)
            self.term_freqs.append(freq)
            self.doc_len.append(len(tokens))
            for term in freq:
                self.doc_freqs[term] += 1
        self.avg_doc_len = total_len / self.N
        for term, df in self.doc_freqs.items():
            # BM25 IDF formula
            self.idf[term] = math.log(1 + (self.N - df + 0.5) / (df + 0.5))

    def search(self, query, top_k=3):
        query_tokens = self._tokenize(query)
        scores = []
        for idx, doc in enumerate(self.documents):
            score = 0
            doc_len = self.doc_len[idx]
            freq = self.term_freqs[idx]
            for term in query_tokens:
                if term in freq:
                    tf = freq[term]
                    idf = self.idf.get(term, 0)
                    numerator = tf * (self.k1 + 1)
                    denominator = tf + self.k1 * \
                        (1 - self.b + self.b * (doc_len / self.avg_doc_len))
                    score += idf * (numerator / denominator)
            scores.append((score, doc))

        scores.sort(reverse=True, key=lambda x: x[0])
        # We only return results with a score > 0 to avoid irrelevant context
        return [s for s in scores[:top_k] if s[0] > 0]


# --- 2. THE DATA LOADER ---
DATA_PATH = "data/raw/nagaland_pages.jsonl"


def load_documents(path):
    documents = []
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                if "text" in data:
                    documents.append(data["text"])
            except:
                continue
    return documents


# --- 3. THE GLOBAL INSTANCE ---
# This runs ONCE when the app starts
_docs = load_documents(DATA_PATH)
_bm25_instance = BM25Retriever(_docs) if _docs else None

# --- 4. THE BRIDGE FUNCTION ---


def search_bm25(query, top_k=3):
    """
    This is what core/pipeline.py calls.
    It returns a list of (score, text) tuples.
    """
    if _bm25_instance:
        return _bm25_instance.search(query, top_k)
    return []
