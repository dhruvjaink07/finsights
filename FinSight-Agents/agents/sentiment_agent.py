class SentimentAgent:
    def __init__(self, news_fetcher, sentiment_analyzer):
        self.news_fetcher = news_fetcher
        self.sentiment_analyzer = sentiment_analyzer

    def fetch_news(self, query, num_articles=10):
        articles = self.news_fetcher.get_news(query, num_articles)
        return articles

    def analyze_sentiment(self, articles):
        sentiments = []
        for article in articles:
            sentiment = self.sentiment_analyzer.analyze(article['content'])
            sentiments.append({
                'title': article['title'],
                'sentiment': sentiment
            })
        return sentiments

    def run(self, query):
        articles = self.fetch_news(query)
        sentiments = self.analyze_sentiment(articles)
        return sentiments