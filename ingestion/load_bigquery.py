import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery


load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "football-analytics-ml")
DATASET_ID = os.getenv("BIGQUERY_RAW_DATASET", "football_raw")
TABLE_ID = os.getenv("BIGQUERY_RAW_TABLE", "raw_fixtures")
INPUT_FILE = Path(
    os.getenv(
        "BIGQUERY_FIXTURES_JSONL",
        "data/raw/fixtures_premier_league_2023_rows.jsonl",
    )
)


def load_jsonl_to_bigquery() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}. "
            "Run ingestion/fetch_data.py and ingestion/prepare_bigquery_jsonl.py first."
        )

    client = bigquery.Client(project=PROJECT_ID)
    dataset_ref = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    client.create_dataset(dataset_ref, exists_ok=True)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
    )

    with open(INPUT_FILE, "rb") as source_file:
        load_job = client.load_table_from_file(
            source_file,
            table_ref,
            job_config=job_config,
        )

    load_job.result()
    table = client.get_table(table_ref)

    print(f"Loaded {table.num_rows} rows into {table_ref}")


if __name__ == "__main__":
    load_jsonl_to_bigquery()
