class BigQueryClient:
    def __init__(self, credentials=None, project=None):
        pass  # No real client

    def query(self, sql):
        # Return dummy data for testing
        return [
            {"symbol": "AAPL", "price": 180.0},
            {"symbol": "GOOGL", "price": 2700.0},
            {"symbol": "MSFT", "price": 320.0},
        ]