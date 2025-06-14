from core.agent_base import BaseAgent, AgentResult
from utils.gemini_helpers import get_gemini_insight

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
        ticker_to_company = {}
        if market_data and isinstance(market_data, list) and len(market_data) > 0:
            first_row = market_data[0]
            for k in first_row.keys():
                if isinstance(k, tuple) and len(k) == 2 and k[0] == 'Close':
                    ticker_to_company[k[1]] = TICKER_TO_COMPANY.get(k[1], k[1])

        for ticker, company in ticker_to_company.items():
            close_price = open_price = volume = None
            if market_data and isinstance(market_data, list) and len(market_data) > 0:
                first_row = market_data[0]
                close_price = first_row.get(('Close', ticker))
                open_price = first_row.get(('Open', ticker))
                volume = first_row.get(('Volume', ticker))
            price_change_pct = None
            trend = "No data"
            if close_price is not None and open_price is not None and open_price != 0:
                price_change_pct = ((close_price - open_price) / open_price) * 100
                trend = "Uptrend" if close_price > open_price else "Downtrend" if close_price < open_price else "Flat"

            sentiments = []
            top_headline = ""
            if company in sentiment_data:
                sentiments = [art['sentiment'] for art in sentiment_data[company]]
                if sentiment_data[company]:
                    top_headline = sentiment_data[company][0]['headline']
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

            # Recommendation logic
            recommendation = "Hold"
            if overall == "Positive" and trend == "Uptrend":
                recommendation = "Buy"
            elif overall == "Negative" and trend == "Downtrend":
                recommendation = "Sell"
            elif overall == "No news":
                recommendation = "Hold"

            # Highlight divergence
            divergence_flag = ""
            if trend == "Uptrend" and overall == "Negative":
                divergence_flag = "⚠️ Price up but sentiment negative! Possible risk or short squeeze."
            elif trend == "Downtrend" and overall == "Positive":
                divergence_flag = "⚠️ Price down but sentiment positive! Possible opportunity or lag."

            # Gemini LLM-powered insight with more context
            prompt = (
                f"Stock: {company} ({ticker})\n"
                f"Latest Close: {close_price}\n"
                f"Latest Open: {open_price}\n"
                f"Price Change: {price_change_pct:.2f}%\n"
                f"Volume: {volume}\n"
                f"Trend: {trend}\n"
                f"Overall Sentiment: {overall}\n"
                f"Headlines: {sentiments}\n"
                f"Top Headline: {top_headline}\n"
                f"Based on this data, provide a one-sentence actionable insight for an investor, including any risks or uncertainties."
            )
            try:
                llm_insight = get_gemini_insight(prompt)
            except Exception as e:
                llm_insight = f"LLM insight unavailable: {e}"

            insights.append({
                "ticker": ticker,
                "company": company,
                "latest_close": close_price,
                "latest_open": open_price,
                "price_change_pct": price_change_pct,
                "trend": trend,
                "volume": volume,
                "overall_sentiment": overall,
                "headline_count": len(sentiments),
                "recommendation": recommendation,
                "divergence_flag": divergence_flag,
                "top_headline": top_headline,
                "llm_insight": llm_insight
            })

        return AgentResult(success=True, data=insights)