import os
from dotenv import load_dotenv
from retrieval.hybrid_retrieval import search_hybrid
from utils.live_fallback import nagaland_live_search
from utils.text_processor import clean_and_tokenize
from reasoning.logic import FactChecker

# 1. Load the secret key from your .env file
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Initialize the Reasoning Engine
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


def answer_query(query):
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
            "raw_evidence": [],
            "verdict": {"verdict": "ERROR", "explanation": "Empty query."}
        }

    # 2️⃣ Retrieval Step
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
            # Format for the reasoning engine (text, score)
            final_evidence = [(live_evidence, 1.0)]
            source_label = "live_wikipedia"

    # 3️⃣ Reasoning Step
    if final_evidence:
        verdict_data = checker.generate_verdict(
            query, final_evidence, api_key=API_KEY)

        return {
            "status": "success",
            "source": source_label,
            "claim": query,
            "raw_evidence": final_evidence,  # 👈 FIXED: Matches your app.py KeyError
            "verdict": verdict_data
        }

    # 4️⃣ Failure State
    return {
        "status": "not_found",
        "source": None,
        "claim": query,
        "raw_evidence": [],
        "verdict": {"verdict": "NOT ENOUGH EVIDENCE", "explanation": "No sources found."}
    }
