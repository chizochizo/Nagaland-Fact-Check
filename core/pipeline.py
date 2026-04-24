import os
from retrieval.bm25_index import search_bm25
from reasoning.logic import FactChecker
from core.live_search import search_google_news, search_youtube_videos

# Initialize the Brain
checker = FactChecker()


def answer_query(query, context_link=None, uploaded_text=None):
    """
    The central bridge that gathers evidence from 3 sources:
    1. Local PDF Database (BM25)
    2. Live Google News
    3. YouTube Video Metadata
    """
    evidence_list = []

    # --- 1. LOCAL RETRIEVAL (BM25) ---
    local_results = search_bm25(query)
    if local_results:
        if isinstance(local_results, list):
            for item in local_results:
                if isinstance(item, tuple) and len(item) > 1:
                    evidence_list.append((0.8, f"LOCAL_PDF: {str(item[1])}"))
        elif isinstance(local_results, str):
            evidence_list.append((0.8, f"LOCAL_PDF: {local_results}"))

    # --- 2. LIVE GOOGLE NEWS SEARCH ---
    news_hits = search_google_news(query)
    for news in news_hits:
        # We give live news a high score (0.9) for current events
        evidence_list.append(
            (0.9, f"NEWS [{news['source']}]: {news['title']} - {news['snippet']} URL: {news['link']}"))

    # --- 3. YOUTUBE VIDEO METADATA ---
    video_hits = search_youtube_videos(query)
    for vid in video_hits:
        # Video metadata is great for visual events
        evidence_list.append(
            (0.7, f"VIDEO [{vid['source']}]: {vid['title']} - {vid['description']} URL: {vid['link']}"))

    # --- 4. MANUAL UPLOAD ---
    if uploaded_text and len(str(uploaded_text).strip()) > 20:
        evidence_list.append((1.0, f"USER_UPLOAD: {str(uploaded_text)}"))

    # --- 5. EXECUTE LOGIC ENGINE ---
    try:
        # If evidence_list is empty, the Hallucination Guard in logic.py
        # will automatically trigger 'NOT ENOUGH INFO'
        result = checker.generate_verdict(query, evidence_list)
        return {"status": "success", "verdict": result}

    except Exception as e:
        return {
            "status": "error",
            "message": f"Pipeline Bridge Error: {str(e)}"
        }
