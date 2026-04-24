import os
import requests
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()


def search_google_news(query):
    print(f"\n🔍 DEBUG: Searching Google News for: {query}...")  # Console Log
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY") or os.getenv("GOOGLE_API_KEY")
    cx = os.getenv("SEARCH_ENGINE_ID")

    if not api_key or not cx:
        print("❌ ERROR: Missing Search API Key or CX ID in .env")
        return []

    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx}&q={query} Nagaland"

    try:
        response = requests.get(url).json()
        results = []
        items = response.get("items", [])
        print(f"✅ DEBUG: Found {len(items)} news articles.")  # Console Log

        for item in items[:3]:
            print(f"   -> Article: {item.get('title')}")  # Console Log
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
                "source": "Google News"
            })
        return results
    except Exception as e:
        print(f"❌ DEBUG: Google News Error: {e}")
        return []


def search_youtube_videos(query):
    print(f"\n🎬 DEBUG: Searching YouTube for: {query}...")  # Console Log
    api_key = os.getenv("YOUTUBE_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("❌ ERROR: Missing YouTube API Key in .env")
        return []

    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        request = youtube.search().list(
            q=f"{query} Nagaland 2026",
            part="snippet",
            type="video",
            maxResults=2
        )
        response = request.execute()

        results = []
        items = response.get("items", [])
        print(f"✅ DEBUG: Found {len(items)} YouTube videos.")  # Console Log

        for item in items:
            print(f"   -> Video: {item['snippet']['title']}")  # Console Log
            results.append({
                "title": item["snippet"]["title"],
                "link": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                "description": item["snippet"]["description"],
                "source": "YouTube"
            })
        return results
    except Exception as e:
        print(f"❌ DEBUG: YouTube Error: {e}")
        return []
