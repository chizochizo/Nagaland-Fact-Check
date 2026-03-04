import os
import json
import numpy as np
import faiss
import nltk  # <--- NEW: For sentence splitting
from sentence_transformers import SentenceTransformer

# Download the sentence tokenizer model
nltk.download('punkt', quiet=True)

MODEL_NAME = 'all-MiniLM-L6-v2'
INDEX_PATH = "data/indexes/nagaland_dense.index"
DATA_PATH = "data/raw/nagaland_pages.jsonl"


class DenseRetriever:
    def __init__(self):
        print(f"🔄 Loading Dense Model: {MODEL_NAME}...")
        self.model = SentenceTransformer(MODEL_NAME)
        self.index = None
        self.documents = []  # This will now store individual SENTENCES

        self._load_or_build_index()

    def _load_or_build_index(self):
        os.makedirs("data/indexes", exist_ok=True)

        # 1. LOAD & SPLIT: We split every page into sentences
        raw_pages = []
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                raw_pages.append(data["text"])

        # <--- NEW LOGIC START --->
        print("✂️ Splitting pages into sentences for better precision...")
        for page in raw_pages:
            sentences = nltk.sent_tokenize(page)
            for s in sentences:
                clean_s = s.strip()
                if len(clean_s) > 20:  # Only keep meaningful sentences
                    self.documents.append(clean_s)
        # <--- NEW LOGIC END --->

        if os.path.exists(INDEX_PATH):
            print("📁 Loading existing Dense Index from disk...")
            self.index = faiss.read_index(INDEX_PATH)
            # IMPORTANT: In a real system, you'd need to ensure self.documents
            # matches the saved index. Since we changed the logic, we must rebuild once.
        else:
            print(
                f"🚀 Building NEW Dense Index with {len(self.documents)} sentences...")
            embeddings = self.model.encode(
                self.documents, show_progress_bar=True, convert_to_numpy=True)

            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype('float32'))

            faiss.write_index(self.index, INDEX_PATH)
            print(f"✅ Dense Index saved to {INDEX_PATH}")

    def search(self, query, top_k=3):
        query_vector = self.model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(
            query_vector.astype('float32'), top_k)

        results = []
        for i in range(len(indices[0])):
            doc_idx = indices[0][i]
            if doc_idx < len(self.documents):
                score = 1 / (1 + distances[0][i])
                results.append((score, self.documents[doc_idx]))

        return results


# Singleton instance for the system
_retriever = None


def search_dense(query, top_k=3):
    global _retriever
    if _retriever is None:
        _retriever = DenseRetriever()
    return _retriever.search(query, top_k)
