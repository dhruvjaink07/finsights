from typing import Dict
from core.agent_base import BaseAgent, AgentResult
# from utils.bigquery_helpers import BigQueryClient  # Unused for now
from utils.yfinance_helper import fetch_stock_data  # <-- Import yfinance helper
import asyncio

class MarketDataAgent(BaseAgent):
    def __init__(self):
        super().__init__("MarketDataAgent")
        # self.bq_client = BigQueryClient()  # Commented: not used in live fetch

    async def execute(self, task: Dict) -> AgentResult:
        task_type = task['task_type']
        params = task['parameters']
        
        try:
            if task_type == "fetch_top_stocks":
                data = await self._fetch_top_stocks(params['count'])
                return AgentResult(success=True, data=data)
            elif task_type == "fetch_specific_stocks":
                data = await self._fetch_specific_stocks(params['symbols'])
                return AgentResult(success=True, data=data)
            # Add other task types...
        except Exception as e:
            return AgentResult(success=False, data=None, error=str(e))

    async def _fetch_top_stocks(self, count: int):
        # Add global and Indian stocks here
        symbols = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS",  # Indian
            "AAPL", "GOOGL", "MSFT",                 # Global (US)
            "TSLA", "AMZN", "META"                   # More US
        ][:count]
        data = fetch_stock_data(symbols)
        return data

    async def _fetch_specific_stocks(self, symbols):
        # symbols: list of tickers (e.g., ["AAPL", "TSLA"])
        data = fetch_stock_data(symbols)
        return data

    # def _fetch_top_stocks_from_bigquery(self, count: int):
    #     # Implementation using your BigQuery helpers (for future use)
    #     pass

    def _clean_data(raw_data: Dict) -> dict:
        return {
            'symbol': raw_data['Symbol'],
            'date': raw_data['Date'].isoformat(),
            'close': round(raw_data['Close'], 2)
        }