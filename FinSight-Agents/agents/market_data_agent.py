class MarketDataAgent:
    def __init__(self, bigquery_client):
        self.bigquery_client = bigquery_client

    def fetch_market_data(self, stock_symbols):
        # Logic to fetch real-time market data for the given stock symbols
        pass

    def store_data_in_bigquery(self, data):
        # Logic to store fetched market data in BigQuery
        pass

    def run(self, stock_symbols):
        market_data = self.fetch_market_data(stock_symbols)
        self.store_data_in_bigquery(market_data)