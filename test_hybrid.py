from core.pipeline import answer_query
import os
import sys

# Ensure root is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_system():
    print("--- 🧬 Nagaland Hybrid System Test (BM25 + Dense) ---")

    test_queries = [
        "What is the capital of Nagaland?",
        "Traditional Naga festivals and culture",
        "How many districts are in Nagaland?"
    ]

    for query in test_queries:
        print(f"\n👉 USER CLAIM: '{query}'")

        result = answer_query(query)

        if result["status"] == "success":
            print(f"✅ Source: {result['source']}")

            # FIX: RRF returns (text, score). We swap them here for clarity.
            for i, (text, score) in enumerate(result["evidence"]):
                # Now 'text' is definitely a string
                snippet = str(text).replace('\n', ' ')[:150] + "..."
                print(f"   [{i+1}] (RRF Score: {score:.4f})")
                print(f"       Content: {snippet}")
        else:
            print(f"❌ {result['evidence']}")


if __name__ == "__main__":
    test_system()
