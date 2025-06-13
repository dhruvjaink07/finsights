import yfinance as yf

def fetch_stock_data(symbols: list) -> list[dict]:
    """
    Fetch stock data for a list of symbols using yfinance.
    
    Args:
        symbols (list): List of stock symbols to fetch data for.
        
    Returns:
        list[dict]: List of dictionaries containing stock data.
    """
    data = yf.download(tickers=symbols, period="1d")
    return data.reset_index().to_dict('records')

def format_for_bigquery(yf_data: list[dict], symbols: list) -> list[dict]:
    """
    Converts yfinance wide-format data to a list of dicts for BigQuery.
    """
    records = []
    for row in yf_data:
        date = row.get('Date')
        for symbol in symbols:
            records.append({
                "symbol": symbol,
                "date": date.isoformat() if hasattr(date, "isoformat") else str(date),
                "close": row.get(('Close', symbol))
            })
    return records

# if __name__ == "__main__":
#     symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
#     result = fetch_stock_data(symbols)
#     print(result)

