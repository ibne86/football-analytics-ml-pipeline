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
* saving raw data locally
* preparing raw data for BigQuery
* loading raw data into BigQuery
* cleaning and transforming data with dbt
* creating staging, intermediate, and mart models
* creating dashboard-ready KPI tables
* validating data quality with dbt tests
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
Future Machine Learning Prediction
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
football_dbt.season_summary
```

---

### 4. dbt Transformation Layer

dbt is used to clean and transform the raw data using SQL.

The dbt layer includes:

* source configuration
* staging models
* intermediate models
* mart models
* schema tests
* custom business-rule tests
* model and column documentation

Example transformations:

* flatten nested API data
* rename unclear columns
* convert date fields
* calculate match outcomes
* create one row per team per match
* calculate wins, draws, losses, goals, goal difference, and points
* create a season-level KPI summary table
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
season_summary
```

The `season_summary` table contains dashboard KPI metrics such as:

* total matches
* total goals
* home wins
* away wins
* draws
* average goals per match

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

The KPI cards use the dbt `season_summary` mart table.
The charts use the dbt mart tables for match, team, and home/away performance analysis.

The dashboard uses the following dbt mart tables:

* `season_summary`
* `match_results`
* `team_performance`
* `home_away_performance`

![Premier League 2023/24 Season Overview](dashboards/powerbi/screenshots/season_overview.png)

---

### 7. Machine Learning Layer

The project now includes an ML-ready dbt mart:

```text
ml_match_features
```

This table contains one row per completed match and includes match identifiers, teams, dates, leakage-safe pre-match features, result labels, goals, and outcome flags.

The table includes a clear prediction target:

```text
target_match_result = Home Win / Draw / Away Win
```

The table also includes pre-match input features that are available before each match starts.

Season-to-date features:

```text
home_matches_played_before
away_matches_played_before
home_points_before
away_points_before
home_avg_points_before
away_avg_points_before
```

Recent-form features:

```text
home_points_last_5
away_points_last_5
home_avg_points_last_5
away_avg_points_last_5
home_goals_for_last_5
away_goals_for_last_5
home_goals_against_last_5
away_goals_against_last_5
```

Future ML features may include:

* home advantage
* league position
* previous match results
* team performance trends

Goal and result columns should be used as labels or evaluation fields, not as predictive input features.

The next ML step is to train a simple baseline model in Python using the safe input features from `ml_match_features`.

---

## ✅ Data Quality and dbt Tests

This project includes dbt tests to validate both basic data quality and football-specific business rules.

### Generic dbt Tests

Generic schema tests are used to check important columns in the mart models.

Examples:

* `match_id` is not null
* `match_id` is unique
* `home_team` and `away_team` are not null
* `match_result` only contains accepted values: `Home Win`, `Away Win`, or `Draw`
* `team_name`, `matches_played`, `wins`, `draws`, `losses`, and `points` are not null
* `season_summary` KPI fields such as `total_matches`, `total_goals`, `home_wins`, `away_wins`, and `draws` are not null

### Custom Business Rule Tests

Custom SQL tests are added to validate football calculations.

The project checks that:

```text
points = wins * 3 + draws
matches_played = wins + draws + losses
goal_difference = goals_for - goals_against
```

These tests help ensure that the final analytics tables are reliable before they are used in Power BI or future machine learning models.

Run all dbt tests with:

```bash
cd dbt_project
dbt test
```

---

## 📚 dbt Documentation

The project includes dbt model and column documentation for:

* staging models
* intermediate models
* mart models
* season summary KPI model

dbt documentation was generated locally using:

```bash
cd dbt_project
dbt docs generate
```

The documentation can be viewed locally with:

```bash
dbt docs serve
```

This helps explain what each dbt model does, how the models relate to each other, and what each important column means.

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
│   ├── models/
│   │   ├── staging/
│   │   │   └── api_football/
│   │   │       ├── _api_football__sources.yml
│   │   │       ├── _api_football__models.yml
│   │   │       └── stg_api_football__fixtures.sql
│   │   │
│   │   ├── intermediate/
│   │   │   ├── _intermediate__models.yml
│   │   │   └── int_team_match_results.sql
│   │   │
│   │   └── marts/
│   │       ├── match_results.sql
│   │       ├── team_performance.sql
│   │       ├── home_away_performance.sql
│   │       ├── season_summary.sql
│   │       ├── ml_match_features.sql
│   │       └── schema.yml
│   │
│   └── tests/
│       ├── assert_team_points_are_correct.sql
│       ├── assert_matches_played_are_correct.sql
│       └── assert_goal_difference_is_correct.sql
│
├── dashboards/
│   └── powerbi/
│       ├── football_analytics_dashboard.pbix
│       ├── README.md
│       └── screenshots/
│           └── season_overview.png
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
* What are the season-level KPI totals?
* What was the average number of goals per match?
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
* dashboard-ready KPI mart creation
* dbt schema testing
* custom dbt business-rule testing
* dbt model and column documentation
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
* season summary mart model created for dashboard KPI metrics
* dbt schema tests added
* custom dbt business-rule tests added
* dbt model and column documentation added
* basic ML-ready feature mart created with `ml_match_features`
* ML prediction target defined with `target_match_result`
* leakage-safe season-to-date ML features added
* leakage-safe recent-form ML features added
* Power BI dashboard created for Premier League 2023/24 season overview
* Power BI KPI cards updated to use the `season_summary` dbt mart table
* dashboard screenshot added to the repository and README

Current focus:

* train a simple baseline ML model in Python
* add automation with GitHub Actions later
* improve dashboard pages over time

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
* [x] Create season summary KPI mart
* [x] Add dbt schema tests
* [x] Add custom dbt business-rule tests
* [x] Add dbt model documentation
* [x] Generate dbt documentation locally

---

### Phase 5: Power BI Dashboard

* [x] Connect Power BI to BigQuery
* [x] Build season overview dashboard
* [x] Build team performance visuals
* [x] Build home vs away analysis
* [x] Use `season_summary` mart for KPI cards
* [x] Add dashboard screenshot to repository
* [x] Add dashboard screenshot to README

---

### Phase 6: Machine Learning

* [x] Create basic ML-ready feature table
* [x] Define prediction target
* [x] Add leakage-safe season-to-date features
* [x] Add leakage-safe recent-form features
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

Generate dbt documentation:

```bash
dbt docs generate
```

Serve dbt documentation locally:

```bash
dbt docs serve
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
→ data quality testing
→ dashboard-ready tables
→ Power BI dashboard
```

The dashboard KPI logic is prepared in dbt using the `season_summary` mart table, while Power BI is used mainly for visualization.

The machine learning layer now has a documented feature mart with a prediction target, season-to-date features, and recent-form features. The next step is to train and evaluate a simple baseline model in Python.

---

## 👤 Author

Created by **Ibne Sina Khan**

This project is part of a portfolio focused on data analytics, cloud data pipelines, automation, and machine learning.
