import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env

FINANCIAL_SOURCES = [
    # Global
    "bloomberg", "financial-times", "business-insider", "cnbc", "the-wall-street-journal", "reuters",
    # Indian
    "the-hindu", "the-times-of-india", "business-standard", "moneycontrol", "livemint", "economic-times"
]
FINANCIAL_KEYWORDS = [
    "stock", "market", "share", "nse", "bse", "exchange", "price", "equity", "ipo", "sensex", "nifty"
]

def fetch_and_process_news(query, num_articles=5):
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        raise ValueError("NEWSAPI_KEY not found in environment variables.")
    # Query for both the term and financial context
    search_query = f"{query} stock OR {query} share OR {query} market"
    sources = ",".join(FINANCIAL_SOURCES)
    url = (
        f"https://newsapi.org/v2/everything?q={search_query}"
        f"&language=en&pageSize={num_articles*2}&sources={sources}&apiKey={api_key}"
    )
    response = requests.get(url)
    response.raise_for_status()
    articles = response.json().get("articles", [])
    # Post-filter for financial keywords
    filtered = [
        {
            "title": a["title"],
            "content": a.get("content"),
            "description": a.get("description"),
            "url": a.get("url"),
            "published_at": a.get("publishedAt"),
            "source": a.get("source", {}).get("name"),
        }
        for a in articles
        if any(kw in (a.get("title", "") + " " + (a.get("description") or "")).lower() for kw in FINANCIAL_KEYWORDS)
    ]
    return filtered[:num_articles]

class NewsFetcherAdapter:
    def get_news(self, query, num_articles):
        return fetch_and_process_news(query, num_articles)

if __name__ == "__main__":
    news = fetch_and_process_news("RELIANCE", num_articles=3)
    for article in news:
        print(article)