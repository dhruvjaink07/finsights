from core.agent_base import BaseAgent, AgentResult
from utils.news_fetcher import NewsFetcherAdapter
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from utils.tickers_to_company import TICKER_TO_COMPANY


class SentimentAgent(BaseAgent):
    def __init__(self, news_fetcher=None, sentiment_analyzer=None):
        super().__init__("SentimentAgent")
        self.news_fetcher = news_fetcher or NewsFetcherAdapter()
        self.sentiment_analyzer = sentiment_analyzer or SentimentIntensityAnalyzer()

    async def execute(self, task):
        symbols = task['parameters'].get('symbols', ['RELIANCE'])
        # Ensure symbols is a list
        if isinstance(symbols, str):
            symbols = [symbols]
        elif isinstance(symbols, list) and len(symbols) == 1 and isinstance(symbols[0], list):
            symbols = symbols[0]  # Handle nested list

        all_results = {}
        for symbol in symbols:
            # Use company name for news search, fallback to symbol if not mapped
            company = TICKER_TO_COMPANY.get(symbol, symbol)
            articles = self.news_fetcher.get_news(company, 10)
            results = []
            for article in articles:
                content = (article.get("title", "") or "") + " " + (article.get("description") or "")
                score = self.sentiment_analyzer.polarity_scores(content)
                label = (
                    "Positive" if score["compound"] > 0.05 else
                    "Negative" if score["compound"] < -0.05 else
                    "Neutral"
                )
                results.append({
                    "headline": article.get("title"),
                    "sentiment": label,
                    "score": round(score["compound"], 2)
                })
            all_results[company] = results  # Use company name as key for clarity
        return AgentResult(success=True, data=all_results)