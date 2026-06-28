# Automation

This document explains how the GitHub Actions automation works for the football analytics pipeline.

The root README gives the short overview. This file keeps the longer automation details.

---

## Workflows

The project has two workflows:

```text
.github/workflows/ci.yml
.github/workflows/full_pipeline.yml
```

## CI Workflow

The CI workflow is a lightweight safety check.

It runs on:

```text
pull requests
pushes to main
```

It checks:

```text
install dependencies
check Python syntax
create a temporary dbt profile
run dbt parse
```

This workflow does not fetch API data, load BigQuery data, run dbt models, or train ML models.

## Full Pipeline Workflow

The full pipeline workflow runs the data engineering pipeline.

It can be started manually from GitHub Actions and is also scheduled to run daily:

```text
06:00 UTC
```

Pipeline steps:

```text
check out repository
install Python dependencies
authenticate to Google Cloud
fetch football data from API-Football
save raw JSON locally on the runner
prepare JSONL for BigQuery
load raw fixtures to BigQuery
run dbt models
run dbt tests
```

The workflow runs on a temporary GitHub-hosted machine. Your local computer does not need to be on.

---

## Required GitHub Secrets

Add these secrets in GitHub:

```text
Repository → Settings → Secrets and variables → Actions
```

Required secrets:

```text
FOOTBALL_API_KEY
GCP_SERVICE_ACCOUNT_KEY
```

`FOOTBALL_API_KEY` is the API-Football key.

`GCP_SERVICE_ACCOUNT_KEY` is the full JSON content of a Google Cloud service account key.

Do not commit these values to Git.

---

## Google Cloud Permissions

The service account needs enough BigQuery permission to:

```text
create or access the raw dataset
load data into the raw fixtures table
create or replace dbt models
run dbt tests against BigQuery tables
```

For a first working portfolio setup, `BigQuery Admin` is simple.

For a stricter production-style setup, reduce permissions later.

---

## BigQuery Load Behavior

The load script is:

```text
ingestion/load_bigquery.py
```

It loads:

```text
data/raw/fixtures_premier_league_2023_rows.jsonl
```

into:

```text
football-analytics-ml.football_raw.raw_fixtures
```

The load uses:

```text
WRITE_TRUNCATE
```

This means each pipeline run replaces the raw fixtures table with the latest fetched file.

That is acceptable for the current project because the source query is fixed to one league and one season, and dbt rebuilds the clean tables from that raw table.

---

## Current API Scope

The API request is configured in:

```text
ingestion/fetch_data.py
```

Current query:

```text
league = 39
season = 2023
```

This means the automated pipeline currently fetches Premier League 2023/24 fixture data.

The pipeline is automated, but the league and season are still configured in code.

A future improvement would be making these values configurable with environment variables.

---

## How to Run Manually

In GitHub:

```text
Actions → Full Pipeline → Run workflow → main → Run workflow
```

Then open the workflow run and check each step.

Successful steps should include:

```text
Authenticate to Google Cloud
Fetch football data
Prepare BigQuery JSONL file
Load raw fixtures to BigQuery
Run dbt models
Run dbt tests
```

---

## What to Check if It Fails

If `Fetch football data` fails:

```text
check FOOTBALL_API_KEY
check API quota or API status
```

If `Authenticate to Google Cloud` fails:

```text
check GCP_SERVICE_ACCOUNT_KEY
make sure the JSON was copied completely
make sure the service account key has not been deleted
```

If `Load raw fixtures to BigQuery` fails:

```text
check service account BigQuery permissions
check project ID and dataset names
```

If `Run dbt models` or `Run dbt tests` fails:

```text
open the failed dbt step
read the model or test error
fix the SQL or data issue
rerun the workflow
```

---

## What Is Not Automated

The current workflow does not automate:

```text
Power BI dashboard refresh
ML model training
MLflow server hosting
```

That is intentional for now. The automated workflow focuses on the data engineering part:

```text
ingestion
raw loading
dbt transformation
dbt validation
```
