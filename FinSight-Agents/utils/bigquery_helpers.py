from google.cloud import bigquery

class BigQueryClient:
    def __init__(self, project=None):
        # No credentials needed for sandbox if you've run gcloud auth application-default login
        self.client = bigquery.Client(project=project)

    def query(self, sql):
        query_job = self.client.query(sql)
        results = query_job.result()
        return [dict(row) for row in results]
    
    def batch_insert(self, table_id: str, records: list[dict]):
        errors = self.client.insert_rows_json(table_id, records)
        if errors:
            raise ValueError(f"BigQuery errors: {errors}")
