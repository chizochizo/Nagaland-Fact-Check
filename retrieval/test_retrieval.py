import json
import os
from retrieval.bm25_index import BM25Retriever, load_documents


def test_retrieval():
    print("📂 --- STEP 1: BM25 RETRIEVAL TEST --- 📂")

    # Path configuration
    data_path = "data/raw/nagaland_pages.jsonl"

    # 1. Check if the database exists
    if not os.path.exists(data_path):
        print(f"❌ ERROR: Database not found at {data_path}")
        print("Please ensure your .jsonl file is in the 'data/raw/' folder.")
        return

    # 2. Load Documents
    print(f"📄 Loading documents from {data_path}...")
    documents = load_documents(data_path)
    print(f"✅ Successfully loaded {len(documents)} document chunks.")

    if len(documents) == 0:
        print("❌ ERROR: No documents found in the file. Check your JSONL formatting.")
        return

    # 3. Initialize BM25
    print("⚙️ Initializing BM25 Index...")
    retriever = BM25Retriever(documents)
    print("✅ Indexing complete.")

    # 4. Test Search
    test_queries = [
        "highest peak in Nagaland",
        "how many districts",
        "Meluri district 2024"
    ]

    for query in test_queries:
        print(f"\n🔍 Searching for: '{query}'")
        results = retriever.search(query, top_k=2)

        if results:
            for i, (score, text) in enumerate(results):
                print(f"   [Result {i+1}] Score: {score:.2f}")
                print(f"   Text: {text[:150]}...")
        else:
            print(f"   ⚠️ No matches found for '{query}'.")

    print("\n🏁 Step 1 Test Finished.")


if __name__ == "__main__":
    test_retrieval()
