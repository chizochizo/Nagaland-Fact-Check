import requests
import time
import json
import os

WIKI_API = "https://en.wikipedia.org/w/api.php"
OUTPUT_FILE = "data/raw/nagaland_pages.jsonl"

os.makedirs("data/raw", exist_ok=True)

HEADERS = {
    "User-Agent": "NagalandKnowledgeBot/1.0 (educational project)"
}

visited_pages = set()
visited_categories = set()


def safe_request(params):
    try:
        response = requests.get(WIKI_API, params=params,
                                headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Request failed:", e)
        return None


def get_category_members(category):
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": "500",
        "format": "json"
    }

    data = safe_request(params)
    if not data:
        return []

    return data.get("query", {}).get("categorymembers", [])


def get_page_content(title):
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": True,
        "titles": title,
        "format": "json"
    }

    data = safe_request(params)
    if not data:
        return ""

    pages = data.get("query", {}).get("pages", {})

    for page_id in pages:
        return pages[page_id].get("extract", "")

    return ""


def crawl_category(category, depth=0, max_depth=7):
    if depth > max_depth:
        return

    if category in visited_categories:
        return

    visited_categories.add(category)

    print(f"Crawling Category: {category} | Depth: {depth}")

    members = get_category_members(category)

    for member in members:
        title = member["title"]

        if title.startswith("Category:"):
            subcategory = title.replace("Category:", "")
            crawl_category(subcategory, depth + 1, max_depth)
        else:
            if title not in visited_pages:
                visited_pages.add(title)
                content = get_page_content(title)

                if content.strip():
                    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                        json.dump({
                            "title": title,
                            "text": content
                        }, f)
                        f.write("\n")

                time.sleep(0.7)  # slow down to avoid block


if __name__ == "__main__":
    crawl_category("Nagaland", max_depth=3)
    print("Done collecting Nagaland pages.")
