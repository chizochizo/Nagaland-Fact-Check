import os
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

# --- TIER 3: GOOGLE CUSTOM SEARCH (Optimized for Zombie Detection) ---


def google_search_live(query):
    """
    Performs a broad search by stripping current year markers.
    This allows the AI to find historical 'Zombie' news from 2018-2024.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        print("⚠️ Google API credentials missing in .env")
        return None

    try:
        # 1. THE ZOMBIE FILTER:
        # We strip '2026' and 'today' so Google finds the ORIGINAL event
        # from past years (2023, 2021, etc.)
        broad_query = query.lower().replace("2026", "").replace("today", "").strip()

        # 2. Connect to Google Search API
        service = build("customsearch", "v1", developerKey=api_key)

        # 3. INCREASE DEPTH:
        # We increase 'num' to 10. This ensures historical news isn't
        # pushed off the first page by 2026 social media noise.
        res = service.cse().list(
            q=broad_query + " Nagaland",
            cx=search_engine_id,
            num=10
        ).execute()

        # 4. DATA ENRICHMENT:
        # We include the 'link' in the snippet so the Logic Engine can
        # see dates directly in the URLs (e.g., /2023/october/...)
        snippets = []
        for item in res.get('items', []):
            snippet = item.get('snippet', '')
            link = item.get('link', '')
            snippets.append(f"[Source: {link}] {snippet}")

        return "\n\n".join(snippets) if snippets else "NO SEARCH RESULTS FOUND."

    except Exception as e:
        print(f"❌ Google Search API Error: {e}")
        return None

# --- TIER 4: YOUTUBE TRANSCRIPT (Nagamese/English) ---


def get_youtube_evidence(url):
    """
    Extracts text from YouTube transcripts to verify video claims.
    """
    try:
        # Extract ID from different YT link formats
        if "v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        else:
            video_id = url.split("/")[-1]

        # Fetch English or Hindi/Nagamese transcripts
        # We prioritize 'en' but fallback to 'hi' if available
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, languages=['en', 'hi']
        )
        full_text = " ".join([entry['text'] for entry in transcript])

        # Limit text to 2000 chars to save RAM and API tokens
        return full_text[:2000]

    except Exception as e:
        print(f"❌ YouTube API Error: {e}")
        return None
