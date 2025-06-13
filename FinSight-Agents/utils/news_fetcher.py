import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env

def fetch_news(api_key, query, from_date=None, to_date=None, language='en'):
    url = f"https://newsapi.org/v2/everything?q={query}&from={from_date}&to={to_date}&language={language}&apiKey={api_key}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json().get('articles', [])
    else:
        raise Exception(f"Error fetching news: {response.status_code} - {response.text}")

def extract_relevant_info(articles):
    relevant_articles = []
    
    for article in articles:
        relevant_info = {
            'title': article.get('title'),
            'description': article.get('description'),
            'url': article.get('url'),
            'published_at': article.get('publishedAt'),
            'source': article.get('source', {}).get('name')
        }
        relevant_articles.append(relevant_info)
    
    return relevant_articles

def fetch_and_process_news(query, num_articles=5):
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        raise ValueError("NEWSAPI_KEY not found in environment variables.")
    url = (
        f"https://newsapi.org/v2/everything?q={query}&language=en&pageSize={num_articles}&apiKey={api_key}"
    )
    response = requests.get(url)
    response.raise_for_status()
    articles = response.json().get("articles", [])
    return [
        {
            "title": a["title"],
            "content": a.get("content"),
            "description": a.get("description"),
            "url": a.get("url"),
            "published_at": a.get("publishedAt"),
            "source": a.get("source", {}).get("name"),
        }
        for a in articles
    ]

if __name__ == "__main__":
    news = fetch_and_process_news("RELIANCE", num_articles=3)
    for article in news:
        print(article)