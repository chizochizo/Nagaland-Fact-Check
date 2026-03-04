import os
import sys

# 1. Ensure the project root is in the Python path for clean imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from retrieval.bm25_retrieval import search_bm25
    print("✅ Imports successful: retrieval.bm25_retrieval is online.")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Ensure you have __init__.py files in your 'retrieval' and 'core' folders.")
    sys.exit(1)


def run_retrieval_test():
    print("\n--- 🛡️  Nagaland BM25 Retrieval Verification ---")

    # 2. Path Check
    data_path = "data/raw/nagaland_pages.jsonl"
    if not os.path.exists(data_path):
        print(f"❌ Error: {data_path} not found.")
        print("💡 Tip: Run your 'nagaland_collector.py' first to gather data!")
        return

    # 3. Define Test Queries
    # These are designed to catch common Naga-specific topics
    test_queries = [
        "Hornbill Festival",
        "Kohima",
        "Nagaland Statehood"
    ]

    for query in test_queries:
        print(f"\n🔍 Searching for: '{query}'")
        try:
            # We use top_k=2 to see the primary and secondary matches
            results = search_bm25(query, top_k=2)

            if not results:
                print(
                    "   ⚠️  No local matches found. Check if the collector file has text.")
                continue

            for i, (score, text) in enumerate(results):
                # We clean up the display text for the terminal
                display_text = text.replace('\n', ' ')[:120] + "..."
                print(f"   [{i+1}] (Score: {score:.4f}) {display_text}")

        except Exception as e:
            print(f"   💥 Search failed with error: {e}")


if __name__ == "__main__":
    run_retrieval_test()
