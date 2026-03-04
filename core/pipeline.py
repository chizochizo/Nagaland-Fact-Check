import re
from retrieval.hybrid_retrieval import search_hybrid
from utils.live_fallback import nagaland_live_search
from utils.text_processor import clean_and_tokenize
from reasoning.logic import FactChecker

# 1. Initialize the Reasoning Engine
checker = FactChecker()

# Nagaland keyword guard for live fallback filtering
NAGALAND_KEYWORDS = [
    "nagaland", "kohima", "dimapur", "mokokchung", "mon",
    "tuensang", "zunheboto", "phek", "wokha", "noklak",
    "niuland", "peren", "kiphire", "longleng", "naga"
]


def is_nagaland_related(query):
    """Checks if the query contains Nagaland-specific keywords."""
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in NAGALAND_KEYWORDS)


def answer_query(query, api_key=None):  # 👈 Added api_key here
    """
    Main Pipeline Flow:
    Clean Query -> Hybrid Retrieval -> Live Fallback -> AI Fact Verdict
    """

    # 1️⃣ Preprocess and Clean
    query_tokens = clean_and_tokenize(query)
    clean_query_str = " ".join(query_tokens)

    if not query_tokens:
        return {
            "status": "error",
            "source": None,
            "claim": query,
            "evidence": "Please provide a valid claim or question."
        }

    # 2️⃣ Retrieval Step (Finding Evidence)
    print(f"🔎 Running Hybrid Search for: {clean_query_str}...")
    local_results = search_hybrid(clean_query_str, top_k=3)

    final_evidence = []
    source_label = None

    if local_results:
        final_evidence = local_results
        source_label = "local_hybrid"
    elif is_nagaland_related(query):
        print(f"🌐 Triggering Live Wikipedia search...")
        live_evidence = nagaland_live_search(clean_query_str)
        if live_evidence:
            final_evidence = [(live_evidence, 1.0)]
            source_label = "live_wikipedia"

    # 3️⃣ Reasoning Step (Generating Verdict via Gemini)
    if final_evidence:
        # Pass the claim, evidence, AND the API key to the checker
        verdict_data = checker.generate_verdict(
            query, final_evidence, api_key=api_key)

        return {
            "status": "success",
            "source": source_label,
            "claim": query,
            "evidence": final_evidence,
            "verdict": verdict_data
        }

    # 4️⃣ Failure State
    return {
        "status": "not_found",
        "source": None,
        "claim": query,
        "evidence": "No relevant evidence found."
    }
