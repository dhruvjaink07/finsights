def fetch_news(api_key, query, from_date=None, to_date=None, language='en'):
    import requests
    from datetime import datetime

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

def fetch_and_process_news(api_key, query, from_date=None, to_date=None, language='en'):
    articles = fetch_news(api_key, query, from_date, to_date, language)
    return extract_relevant_info(articles)