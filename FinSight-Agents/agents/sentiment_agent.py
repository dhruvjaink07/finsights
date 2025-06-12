from core.agent_base import BaseAgent, AgentResult

class SentimentAgent(BaseAgent):
    def __init__(self, news_fetcher, sentiment_analyzer):
        super().__init__("SentimentAgent")
        self.news_fetcher = news_fetcher
        self.sentiment_analyzer = sentiment_analyzer

    async def execute(self, task):
        query = task['parameters'].get('query', 'AAPL')
        articles = self.news_fetcher.get_news(query, 10)
        sentiments = []
        for article in articles:
            sentiment = self.sentiment_analyzer.analyze(article['content'])
            sentiments.append({
                'title': article['title'],
                'sentiment': sentiment
            })
        return AgentResult(success=True, data=sentiments)