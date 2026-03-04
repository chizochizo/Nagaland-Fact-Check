import requests

SEARCH_API = "https://en.wikipedia.org/w/api.php"
SUMMARY_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"

# IMPORTANT: Always send User-Agent to Wikipedia to avoid being blocked
HEADERS = {
    "User-Agent": "NagalandKnowledgeBot/1.0 (contact: your_email@example.com)"
}

NAGALAND_KEYWORDS = [
    "nagaland", "kohima", "dimapur", "mokokchung", "mon district",
    "tuensang", "zunheboto", "phek", "wokha", "noklak",
    "niuland", "peren", "kiphire", "longleng",
    "chief minister of nagaland", "governor of nagaland"
]


def search_wikipedia(query):
    """Search Wikipedia and return best matching page title."""
    try:
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json"
        }
        response = requests.get(SEARCH_API, params=params,
                                headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return None

        data = response.json()
        results = data.get("query", {}).get("search", [])
        return results[0]["title"] if results else None
    except Exception as e:
        print(f"Search failed: {e}")
        return None


def fetch_summary(title):
    """Fetch summary of a Wikipedia page."""
    try:
        # Wikipedia API expects underscores instead of spaces
        clean_title = title.replace(" ", "_")
        response = requests.get(
            SUMMARY_API + clean_title,
            headers=HEADERS,
            timeout=10
        )
        if response.status_code != 200:
            return None, None

        data = response.json()
        return data.get("title", ""), data.get("extract", "")
    except Exception as e:
        print(f"Summary fetch failed: {e}")
        return None, None


def is_nagaland_related(title, summary):
    """Security check to ensure the Wikipedia page is actually about Nagaland."""
    if not title or not summary:
        return False
    combined_text = (title + " " + summary).lower()
    return any(keyword in combined_text for keyword in NAGALAND_KEYWORDS)


def nagaland_live_search(query):
    """
    The main fallback function used by pipeline.py
    """
    page_title = search_wikipedia(query)
    if not page_title:
        return None

    title, summary = fetch_summary(page_title)
    if summary and is_nagaland_related(title, summary):
        return summary

    return None
