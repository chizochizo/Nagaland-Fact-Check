import os
import json
from reasoning.logic import FactChecker
from dotenv import load_dotenv

# Load your API Key
load_dotenv()


def test_logic():
    print("🧠 --- STEP 2: GEMINI LOGIC & JSON TEST --- 🧠")

    checker = FactChecker()

    # We will simulate the BM25 result we just saw for Meluri
    mock_evidence = [
        (11.05, "Meluri district was notified as the 17th district of Nagaland on November 2, 2024.")
    ]

    # Test 1: Standard English Claim (Thinking Budget should be 0)
    print("\n📝 Test 1: English Claim (Fast Mode)")
    claim_1 = "Nagaland has 17 districts."

    # Test 2: Nagamese/Mixed Claim (Thinking Budget should be -1)
    print("\n🌏 Test 2: Nagamese Claim (Deep Thinking Mode)")
    claim_2 = "Nagaland te 17 districts ase na?"

    for i, claim in enumerate([claim_1, claim_2]):
        print(f"--- Running Sub-test {i+1} ---")
        try:
            result = checker.generate_verdict(claim, mock_evidence)

            # Print the raw response keys to verify structure
            print(f"✅ Received Keys: {list(result.keys())}")
            print(f"⚖️ Verdict: {result.get('verdict')}")
            print(f"📊 Confidence: {result.get('confidence')}%")
            print(f"📖 Summary: {result.get('evidence_summary')[:100]}...")

        except Exception as e:
            print(f"❌ ERROR in Sub-test {i+1}: {str(e)}")

    print("\n🏁 Step 2 Test Finished.")


if __name__ == "__main__":
    test_logic()
