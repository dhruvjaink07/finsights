def get_bigquery_client():
    from google.cloud import bigquery

    # Create a BigQuery client
    client = bigquery.Client()
    return client

def create_dataset(dataset_name):
    client = get_bigquery_client()
    dataset = bigquery.Dataset(client.dataset(dataset_name))
    dataset.location = "US"  # Set the location as needed

    # Create the dataset
    dataset = client.create_dataset(dataset, exists_ok=True)
    return dataset

def upload_dataframe_to_bigquery(dataframe, table_id):
    client = get_bigquery_client()

    # Upload the DataFrame to BigQuery
    job = client.load_table_from_dataframe(dataframe, table_id)
    job.result()  # Wait for the job to complete

    return job

def query_bigquery(query):
    client = get_bigquery_client()

    # Execute the query
    query_job = client.query(query)
    results = query_job.result()  # Wait for the job to complete

    return results

def delete_table(table_id):
    client = get_bigquery_client()

    # Delete the specified table
    client.delete_table(table_id, not_found_ok=True)