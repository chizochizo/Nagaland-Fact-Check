from retrieval.hybrid_retrieval import search_hybrid
from retrieval.cross_reranker import rerank_results
from reasoning.logic import FactChecker
from core.live_search import search_google_news, search_youtube_videos

import re
import datetime

# Initialize Logic Engine
checker = FactChecker()


# -------------------------------
# 🔍 ENTITY EXTRACTION (SAFE)
# -------------------------------
def extract_entities(text):
    if not isinstance(text, str):
        return set()
    return set(re.findall(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b", text))


# -------------------------------
# 📅 DATE DETECTION
# -------------------------------
def detect_year(text):
    if not isinstance(text, str):
        return []
    return re.findall(r"\b(19\d{2}|20\d{2})\b", text)


# -------------------------------
# 🧠 EVIDENCE SCORING (UPGRADED)
# -------------------------------
def score_evidence(query, text, base_score):

    # --- SAFETY ---
    if not isinstance(text, str):
        text = str(text)

    try:
        score = float(base_score)
    except:
        score = 0.5

    query_lower = query.lower()
    text_lower = text.lower()

    # --- ENTITY MATCH ---
    query_entities = extract_entities(query)
    text_entities = extract_entities(text)

    matches = query_entities.intersection(text_entities)
    if matches:
        score += 0.3 * len(matches)

    # --- DATE LOGIC (🔥 CRITICAL FIX) ---
    current_year = str(datetime.date.today().year)
    years = detect_year(text)

    if current_year in years:
        score += 0.7  # strong boost
    elif years:
        score -= 0.6  # strong penalty for old info
    else:
        score -= 0.4  # ❗ NO DATE = suspicious

    # --- SOURCE TYPE CONTROL ---
    if text.startswith("NEWS"):
        score += 0.5  # ✅ trusted source

    if text.startswith("LOCAL"):
        score += 0.3  # good but not perfect

    if text.startswith("VIDEO"):
        # ❌ videos are unreliable unless date is clear
        if not years:
            score -= 0.7
        else:
            score -= 0.3

    # --- NOISE FILTER ---
    noise_words = [
        "album", "song", "movie", "film",
        "novel", "character", "biography"
    ]

    if any(word in text_lower for word in noise_words):
        score -= 0.8

    return score


# -------------------------------
# 🧹 CLEAN DUPLICATES
# -------------------------------
def clean_evidence(evidence_list):
    seen = set()
    cleaned = []

    for score, text in evidence_list:
        key = str(text)[:200]
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
    hybrid_results = search_hybrid(query, top_k=10)

    for text, base_score in hybrid_results:
        score = score_evidence(query, text, base_score)
        evidence_list.append((score, f"LOCAL: {text}"))

    # --- 2. GOOGLE NEWS ---
    news_hits = search_google_news(query)
    for news in news_hits:
        text = f"NEWS: {news['title']} - {news['snippet']} URL: {news['link']}"
        score = score_evidence(query, text, 1.0)
        evidence_list.append((score, text))

    # --- 3. YOUTUBE (DOWNGRADED ROLE) ---
    video_hits = search_youtube_videos(query)
    for vid in video_hits:
        text = f"VIDEO: {vid['title']} - {vid['description']}"
        score = score_evidence(query, text, 0.4)  # lower base
        evidence_list.append((score, text))

    # --- 4. USER UPLOAD ---
    if uploaded_text and len(uploaded_text.strip()) > 20:
        score = score_evidence(query, uploaded_text, 1.2)
        evidence_list.append((score, f"USER: {uploaded_text}"))

    # --- 5. CLEAN ---
    evidence_list = clean_evidence(evidence_list)

    # --- 6. SORT BEFORE RERANK ---
    evidence_list.sort(key=lambda x: x[0], reverse=True)

    # --- 7. CROSS-ENCODER RERANK ---
    try:
        evidence_list = rerank_results(query, evidence_list, top_k=10)
    except Exception as e:
        print(f"⚠️ Reranker failed: {e}")

    # --- 8. FINAL LIMIT ---
    evidence_list = evidence_list[:7]

    # --- 9. EXTRACT TEXT ---
    final_evidence = [text for _, text in evidence_list]

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
