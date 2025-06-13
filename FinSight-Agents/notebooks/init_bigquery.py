from google.cloud import bigquery
import json
import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.yfinance_helper import fetch_stock_data, format_for_bigquery
from utils.bigquery_helpers import BigQueryClient

# Load schema from JSON file
schema_path = os.path.join(os.path.dirname(__file__), '../data/schemas/market_data.json')
with open(schema_path, 'r') as f:
    schema_json = json.load(f)

# Convert JSON schema to bigquery.SchemaField objects
schema = [bigquery.SchemaField(field['name'], field['type'], mode=field.get('mode', 'NULLABLE')) for field in schema_json]

client = bigquery.Client()
dataset_id = 'market_data'  # Change if your dataset is named differently
table_id = 'stock_prices'

table_ref = client.dataset(dataset_id).table(table_id)
table = bigquery.Table(table_ref, schema=schema)

# Create the table (ignore if it already exists)
try:
    client.create_table(table)
    print(f"Table {dataset_id}.{table_id} created.")
except Exception as e:
    print(f"Table {dataset_id}.{table_id} may already exist or error: {e}")

if __name__ == "__main__":
    symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
    yf_data = fetch_stock_data(symbols)
    records = format_for_bigquery(yf_data, symbols)

    print("Sample record to insert:", records[0] if records else "No data!")

    # Ensure the processed data directory exists
    csv_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/processed'))
    os.makedirs(csv_dir, exist_ok=True)
    csv_path = os.path.join(csv_dir, 'stock_data.csv')

    # Save records as CSV for manual upload to BigQuery
    df = pd.DataFrame(records)
    df.to_csv(csv_path, index=False)
    print(f"Saved {len(records)} records to {csv_path}")

    # --- Uncomment below to use BigQuery streaming insert (not allowed in sandbox) ---
    # bq = BigQueryClient()
    # table_id = "market_data.stock_prices"  # dataset.table
    # bq.batch_insert(table_id, records)
    # print("Data pushed to BigQuery!")