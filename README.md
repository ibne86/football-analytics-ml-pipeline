<div align="center">

# ⚽ Football Analytics & ML Pipeline

**End-to-end football data pipeline for data collection, cloud storage, SQL transformation, analytics dashboards, and machine learning-based match prediction.**

<br>

![Python](https://img.shields.io/badge/PYTHON-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![BigQuery](https://img.shields.io/badge/BIGQUERY-4285F4?style=for-the-badge\&logo=googlecloud\&logoColor=white)
![dbt](https://img.shields.io/badge/DBT-FF694B?style=for-the-badge\&logo=dbt\&logoColor=white)
![Power BI](https://img.shields.io/badge/POWER%20BI-F2C811?style=for-the-badge\&logo=powerbi\&logoColor=black)
![Machine Learning](https://img.shields.io/badge/MACHINE%20LEARNING-102230?style=for-the-badge)
![GitHub Actions](https://img.shields.io/badge/GITHUB%20ACTIONS-2088FF?style=for-the-badge\&logo=githubactions\&logoColor=white)

</div>

---

## 📌 Project Overview

This project demonstrates an end-to-end football analytics and machine learning pipeline.

The goal is to collect football match data from an API, store raw data in BigQuery, transform it into clean analytics-ready tables using dbt, build Power BI dashboards, and prepare the data for machine learning-based match prediction.

In simple words, this project shows the full data journey:

```text
Raw football data
→ cloud storage
→ clean transformed data
→ analytics tables
→ dashboard insights
→ ML-ready dataset
```

---

## 🎯 Project Purpose

This project is designed as a portfolio project to demonstrate practical data skills across the full pipeline.

It focuses on:

* collecting football data from an API
* saving raw data
* loading raw data into BigQuery
* cleaning and transforming data with dbt
* preparing analytics-ready tables
* building dashboard-ready datasets
* creating a Power BI dashboard
* preparing future machine learning features
* documenting the project clearly on GitHub

This is not only a dashboard project.
It is a complete data pipeline project.

---

## 🏗️ Pipeline Architecture

```text
Football API
    ↓
Python Data Ingestion
    ↓
Raw JSON / JSONL Files
    ↓
BigQuery Raw Tables
    ↓
dbt SQL Transformations
    ↓
BigQuery Clean Analytics Tables
    ↓
Power BI Dashboard
    ↓
Machine Learning Prediction
```

---

## 🧱 Main Pipeline Stages

### 1. Data Ingestion

Python scripts collect football data from API-Football.

Example data includes:

* match results
* teams
* leagues
* match dates
* home and away teams
* goals scored
* venues
* match status

The ingestion layer fetches raw API data and saves it locally before loading it into BigQuery.

---

### 2. Raw Data Layer

The raw data is stored before cleaning or transformation.

This is useful because it keeps the original API response available for:

* debugging
* validation
* reprocessing
* checking data quality
* comparing raw and clean data

Example folder:

```text
data/raw/
```

The raw fixture data is also converted into JSONL format before being loaded into BigQuery.

---

### 3. BigQuery Storage Layer

Google BigQuery is used as the cloud data warehouse.

The project uses two main BigQuery datasets:

```text
football_raw
football_dbt
```

`football_raw` stores the raw API data.

`football_dbt` stores the cleaned and transformed dbt models.

Example raw table:

```text
football_raw.raw_fixtures
```

Example transformed tables:

```text
football_dbt.stg_api_football__fixtures
football_dbt.match_results
football_dbt.int_team_match_results
football_dbt.team_performance
football_dbt.home_away_performance
```

---

### 4. dbt Transformation Layer

dbt is used to clean and transform the raw data using SQL.

The dbt layer includes:

* staging models
* intermediate models
* mart models
* schema tests

Example transformations:

* flatten nested API data
* rename unclear columns
* convert date fields
* calculate match outcomes
* create team-level performance rows
* calculate wins, draws, losses, goals, goal difference, and points
* prepare dashboard-ready tables

dbt helps separate raw data from clean analytical data.

---

### 5. Analytics Layer

Clean tables are created for analysis and reporting.

Current analytics tables:

```text
match_results
team_performance
home_away_performance
```

These tables are used in Power BI for dashboard reporting.

---

### 6. Power BI Dashboard Layer

The project includes a Power BI dashboard built from the clean BigQuery tables created by dbt.

The first dashboard page provides a Premier League 2023/24 season overview, including:

* Total matches
* Total goals
* Home wins
* Away wins
* Draws
* Points by team
* Goals scored by team
* Home vs away points comparison

The dashboard uses the following dbt mart tables:

* `match_results`
* `team_performance`
* `home_away_performance`

![Premier League 2023/24 Season Overview](dashboards/powerbi/screenshots/season_overview.png)

---

### 7. Machine Learning Layer

The cleaned data will later be prepared for machine learning.

Possible prediction target:

```text
Predict match result: home win / draw / away win
```

Possible ML features:

* home team recent form
* away team recent form
* goals scored
* goals conceded
* home advantage
* league position
* previous match results
* team performance trends

The ML layer will be added after the analytics pipeline and dashboard layer are stable.

---

## 🛠️ Tech Stack

| Area                 | Tools              |
| -------------------- | ------------------ |
| Programming          | Python             |
| Data Source          | API-Football       |
| Raw Storage          | Local JSON / JSONL |
| Cloud Data Warehouse | Google BigQuery    |
| Transformation       | dbt                |
| Dashboard            | Power BI           |
| Machine Learning     | Scikit-learn       |
| Automation           | GitHub Actions     |
| Version Control      | Git & GitHub       |

---

## 📂 Project Structure

```text
football-analytics-ml-pipeline/
├── ingestion/
│   ├── fetch_data.py
│   └── prepare_bigquery_jsonl.py
│
├── data/
│   └── raw/
│       └── .gitkeep
│
├── dbt_project/
│   ├── dbt_project.yml
│   └── models/
│       ├── staging/
│       │   └── api_football/
│       │       ├── _api_football__sources.yml
│       │       └── stg_api_football__fixtures.sql
│       │
│       ├── intermediate/
│       │   └── int_team_match_results.sql
│       │
│       └── marts/
│           ├── match_results.sql
│           ├── team_performance.sql
│           ├── home_away_performance.sql
│           └── schema.yml
│
├── dashboards/
│   └── powerbi/
│       ├── football_analytics_dashboard.pbix
│       ├── README.md
│       └── screenshots/
│           └── season_overview.png
│
├── ml/
│   └── train_model.py
│
├── .github/
│   └── workflows/
│
├── README.md
└── requirements.txt
```

---

## 📊 Example Analysis Questions

This project can answer questions such as:

* Which teams scored the most goals?
* Which teams earned the most points?
* Which teams performed better at home?
* Which teams performed better away?
* Which teams had the strongest goal difference?
* How many matches ended in home wins, away wins, and draws?
* Can match outcomes be predicted from team statistics?

---

## 🧠 What This Project Demonstrates

This project demonstrates practical data and engineering skills:

* API data extraction
* Python scripting
* working with raw JSON data
* preparing JSONL data for BigQuery
* cloud data warehousing
* SQL transformation
* dbt data modeling
* staging, intermediate, and mart model design
* dbt schema testing
* dashboard data preparation
* Power BI dashboard creation
* machine learning feature preparation
* GitHub documentation
* branch-based development workflow

---

## ✅ Current Status

The project currently has a working end-to-end analytics pipeline.

Completed:

* GitHub repository created
* API-Football data ingestion script added
* raw fixture data saved locally
* raw fixture data prepared as JSONL
* raw fixture data loaded into BigQuery
* dbt project connected to BigQuery
* staging model created for raw fixtures
* intermediate model created for team-level match rows
* mart models created for match results, team performance, and home/away performance
* dbt schema tests added
* Power BI dashboard created for Premier League 2023/24 season overview
* dashboard screenshot added to the repository

Current focus:

* improve dashboard documentation
* prepare future ML feature tables
* add automation with GitHub Actions later

---

## 🗺️ Roadmap

### Phase 1: Project Setup

* [x] Create GitHub repository
* [x] Create basic project structure
* [x] Add README file
* [x] Add requirements file
* [x] Add raw data folder

---

### Phase 2: Data Ingestion

* [x] Select football API
* [x] Create API key
* [x] Write Python script to fetch data
* [x] Save raw API response locally
* [x] Add environment variable support for API key
* [x] Prepare JSONL file for BigQuery loading

---

### Phase 3: BigQuery Storage

* [x] Create Google Cloud project
* [x] Create BigQuery dataset
* [x] Create raw fixtures table
* [x] Load raw football data into BigQuery
* [x] Validate loaded data

---

### Phase 4: dbt Transformations

* [x] Set up dbt project
* [x] Connect dbt to BigQuery
* [x] Create source configuration
* [x] Create staging model
* [x] Create intermediate model
* [x] Create final mart tables
* [x] Add dbt tests
* [ ] Generate dbt documentation

---

### Phase 5: Power BI Dashboard

* [x] Connect Power BI to BigQuery
* [x] Build season overview dashboard
* [x] Build team performance visuals
* [x] Build home vs away analysis
* [x] Add dashboard screenshot to repository
* [x] Add dashboard screenshot to README

---

### Phase 6: Machine Learning

* [ ] Create ML feature table
* [ ] Define prediction target
* [ ] Train baseline model
* [ ] Evaluate model performance
* [ ] Compare model results
* [ ] Document ML findings

---

### Phase 7: Automation

* [ ] Add GitHub Actions workflow
* [ ] Automate data ingestion
* [ ] Automate validation steps
* [ ] Automate dbt transformations

---

## ▶️ How to Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the data ingestion script:

```bash
python ingestion/fetch_data.py
```

Prepare the JSONL file for BigQuery:

```bash
python ingestion/prepare_bigquery_jsonl.py
```

Run dbt models:

```bash
cd dbt_project
dbt run
```

Run dbt tests:

```bash
dbt test
```

---

## 🔐 Environment Variables

API keys should not be written directly in the code.

The project uses an environment variable:

```text
FOOTBALL_API_KEY
```

This keeps sensitive keys outside the source code.

Example `.env` file:

```text
FOOTBALL_API_KEY=your_api_key_here
```

The `.env` file is ignored by Git and should not be pushed to GitHub.

---

## 📌 Notes

This project is being built step by step.

The current version focuses on:

```text
API data collection
→ raw data storage
→ BigQuery loading
→ dbt transformation
→ dashboard-ready tables
→ Power BI dashboard
```

The machine learning layer will be added after the analytics pipeline and dashboard layer are stable.

---

## 👤 Author

Created by **Ibne Sina Khan**

This project is part of a portfolio focused on data analytics, cloud data pipelines, automation, and machine learning.
