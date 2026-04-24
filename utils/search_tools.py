import os
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

# --- TIER 3: GOOGLE CUSTOM SEARCH ---


def google_search_live(query):
    api_key = os.getenv("GOOGLE_API_KEY")
    search_engine_id = os.getenv("SEARCH_ENGINE_ID")

    if not api_key or not search_engine_id:
        print("⚠️ Google API credentials missing in .env")
        return None

    try:
        # Connect to Google Search API
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query + " Nagaland", cx=search_engine_id, num=3).execute()

        # Merge top 3 snippets into a single evidence string
        snippets = [item.get('snippet', '') for item in res.get('items', [])]
        return "\n".join(snippets) if snippets else None
    except Exception as e:
        print(f"❌ Google Search API Error: {e}")
        return None

# --- TIER 4: YOUTUBE TRANSCRIPT (Nagamese/English) ---


def get_youtube_evidence(url):
    try:
        # Extract ID from different YT link formats
        if "v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        else:
            video_id = url.split("/")[-1]

        # Fetch English or Hindi/Nagamese transcripts
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, languages=['en', 'hi'])
        full_text = " ".join([entry['text'] for entry in transcript])

        # Limit text to 2000 chars to save RAM
        return full_text[:2000]
    except Exception as e:
        print(f"❌ YouTube API Error: {e}")
        return None
