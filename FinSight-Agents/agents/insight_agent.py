from core.agent_base import BaseAgent, AgentResult

# Make sure this mapping matches what you use in SentimentAgent
TICKER_TO_COMPANY = {
    "RELIANCE.NS": "Reliance",
    "TCS.NS": "TCS",
    "HDFCBANK.NS": "HDFC Bank",
    "INFY.NS": "Infosys",
    "ICICIBANK.NS": "ICICI Bank",
    "SBIN.NS": "State Bank of India",
    "BHARTIARTL.NS": "Bharti Airtel",
    "ITC.NS": "ITC",
    "LT.NS": "Larsen & Toubro",
    "AXISBANK.NS": "Axis Bank",
    "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "BAJFINANCE.NS": "Bajaj Finance",
    "ASIANPAINT.NS": "Asian Paints",
    "MARUTI.NS": "Maruti Suzuki",
    "SUNPHARMA.NS": "Sun Pharma",
    "ULTRACEMCO.NS": "UltraTech Cement",
    "TITAN.NS": "Titan",
    "WIPRO.NS": "Wipro",
    "POWERGRID.NS": "Power Grid",
    # Global
    "AAPL": "Apple",
    "GOOGL": "Google",
    "MSFT": "Microsoft",
    "TSLA": "Tesla",
    "AMZN": "Amazon",
    "META": "Meta",
    # Add more mappings as needed
}

class InsightAgent(BaseAgent):
    def __init__(self, sentiment_data, market_data):
        super().__init__("InsightAgent")
        self.sentiment_data = sentiment_data
        self.market_data = market_data

    async def execute(self, task):
        market_data = task['parameters'].get('market_data', [])
        sentiment_data = task['parameters'].get('sentiment', {})

        insights = []
        # Build a mapping from ticker to company name
        ticker_to_company = {}
        if market_data and isinstance(market_data, list) and len(market_data) > 0:
            first_row = market_data[0]
            for k in first_row.keys():
                if isinstance(k, tuple) and len(k) == 2 and k[0] == 'Close':
                    ticker_to_company[k[1]] = TICKER_TO_COMPANY.get(k[1], k[1])

        # Always generate an insight for every ticker in market data
        for ticker, company in ticker_to_company.items():
            # Get latest close price
            close_price = None
            if market_data and isinstance(market_data, list) and len(market_data) > 0:
                first_row = market_data[0]
                close_price = first_row.get(('Close', ticker))
            # Aggregate sentiment
            sentiments = []
            if company in sentiment_data:
                sentiments = [art['sentiment'] for art in sentiment_data[company]]
            if sentiments:
                pos = sentiments.count('Positive')
                neg = sentiments.count('Negative')
                neu = sentiments.count('Neutral')
                if pos > neg and pos > neu:
                    overall = "Positive"
                elif neg > pos and neg > neu:
                    overall = "Negative"
                else:
                    overall = "Neutral"
            else:
                overall = "No news"
            insights.append({
                "ticker": ticker,
                "company": company,
                "latest_close": close_price,
                "overall_sentiment": overall,
                "headline_count": len(sentiments)
            })

        return AgentResult(success=True, data=insights)