from retrieval.hybrid_retrieval import search_hybrid
from retrieval.cross_reranker import rerank_results
from reasoning.logic import FactChecker
from core.live_search import search_google_news, search_youtube_videos

import re
import datetime

checker = FactChecker()


# -------------------------------
# 🔍 ENTITY EXTRACTION (FIXED)
# -------------------------------
def extract_entities(text):
    if not isinstance(text, str):   # ✅ FIX
        return set()
    return set(re.findall(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b", text))


# -------------------------------
# 📅 DATE DETECTION
# -------------------------------
def detect_year(text):
    if not isinstance(text, str):   # ✅ FIX
        return []
    return re.findall(r"\b(19\d{2}|20\d{2})\b", text)


# -------------------------------
# 🧠 EVIDENCE SCORING
# -------------------------------
def score_evidence(query, text, base_score):

    # ✅ HARD TYPE SAFETY
    if not isinstance(text, str):
        return 0.0

    try:
        score = float(base_score)
    except:
        score = 0.5

    query_entities = extract_entities(query)
    text_entities = extract_entities(text)

    # --- ENTITY MATCH BOOST ---
    matches = query_entities.intersection(text_entities)
    if matches:
        score += 0.3 * len(matches)

    # --- DATE LOGIC ---
    current_year = str(datetime.date.today().year)
    years = detect_year(text)

    if current_year in years:
        score += 0.5
    elif years:
        score -= 0.4

    # --- NOISE FILTER ---
    noise_words = [
        "album", "song", "movie", "film",
        "novel", "character", "born", "biography"
    ]

    if any(word in text.lower() for word in noise_words):
        score -= 0.6

    return score


# -------------------------------
# 🧹 CLEAN DUPLICATES (SAFE)
# -------------------------------
def clean_evidence(evidence_list):
    seen = set()
    cleaned = []

    for score, text in evidence_list:
        if not isinstance(text, str):
            continue  # ✅ DROP CORRUPT DATA

        key = text[:200]
        if key not in seen:
            seen.add(key)
            cleaned.append((score, text))

    return cleaned


# -------------------------------
# 🚀 MAIN PIPELINE
# -------------------------------
def answer_query(query, context_link=None, uploaded_text=None):

    evidence_list = []

    # --- 1. HYBRID RETRIEVAL ---
    hybrid_results = search_hybrid(query, top_k=7)

    for text, base_score in hybrid_results:
        if not isinstance(text, str):   # ✅ SAFETY
            continue

        improved_score = score_evidence(query, text, base_score)
        evidence_list.append((improved_score, f"LOCAL: {text}"))

    # --- 2. GOOGLE NEWS ---
    news_hits = search_google_news(query)
    for news in news_hits:
        text = f"NEWS: {news['title']} - {news['snippet']} URL: {news['link']}"
        score = score_evidence(query, text, 0.9)
        evidence_list.append((score, text))

    # --- 3. YOUTUBE ---
    video_hits = search_youtube_videos(query)
    for vid in video_hits:
        text = f"VIDEO: {vid['title']} - {vid['description']}"
        score = score_evidence(query, text, 0.6)
        evidence_list.append((score, text))

    # --- 4. USER UPLOAD ---
    if uploaded_text and isinstance(uploaded_text, str) and len(uploaded_text.strip()) > 20:
        score = score_evidence(query, uploaded_text, 1.0)
        evidence_list.append((score, f"USER: {uploaded_text}"))

    # --- 5. CLEAN ---
    evidence_list = clean_evidence(evidence_list)

    # --- 6. SORT ---
    evidence_list.sort(
        key=lambda x: x[0] if isinstance(x[0], (int, float)) else 0,
        reverse=True
    )

    # --- 7. RERANK ---
    try:
        evidence_list = rerank_results(query, evidence_list, top_k=10)
    except Exception as e:
        print(f"⚠️ Reranker failed: {e}")

    # --- 8. FINAL LIMIT ---
    evidence_list = evidence_list[:7]

    # --- 9. FINAL SAFE EXTRACTION ---
    final_evidence = []
    for item in evidence_list:
        if isinstance(item, tuple) and len(item) == 2:
            score, text = item
            if isinstance(text, str):
                final_evidence.append(text)

    # --- 10. FACT CHECK ---
    try:
        result = checker.generate_verdict(query, final_evidence)
        return {
            "status": "success",
            "verdict": result,
            "evidence": evidence_list
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Pipeline Error: {str(e)}"
        }
