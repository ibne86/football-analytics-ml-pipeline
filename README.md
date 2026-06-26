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
* creating ML-ready features and evaluating baseline models
* tracking ML experiments locally with MLflow
* running CI checks and full pipeline automation with GitHub Actions
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
Machine Learning Model Evaluation
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

The first Python ML step uses these safe input features to train and evaluate simple classification models.

### ML Model Training and Evaluation Scripts

The project includes Python ML training and evaluation scripts:

```text
ml/train_baseline_model.py
ml/train_balanced_logistic_regression.py
ml/train_random_forest_model.py
ml/evaluate_stratified_k_fold.py
ml/tune_random_forest_grid_search.py
```

`train_baseline_model.py` trains the original Logistic Regression baseline without class weighting.

`train_balanced_logistic_regression.py` trains Logistic Regression with:

```text
class_weight = balanced
```

The balanced model was added because the original baseline did not predict draws well.

`train_random_forest_model.py` trains a Random Forest classifier as the first non-linear comparison model.

`evaluate_stratified_k_fold.py` compares the models using Stratified K-Fold cross-validation.

`tune_random_forest_grid_search.py` tunes the Random Forest model using GridSearchCV.

The models predict:

```text
target_match_result
```

The models use only leakage-safe pre-match input features from `ml_match_features`.

Outcome and reference columns are intentionally excluded from model inputs:

```text
home_goals
away_goals
total_goals
match_result
target_match_result
is_home_win
is_away_win
is_draw
```

The original baseline result:

```text
Majority-class accuracy:      0.461
Logistic Regression accuracy: 0.513
```

The original Logistic Regression baseline performs better than always predicting the most common result, but it does not predict draws well.

The balanced Logistic Regression model improves draw handling, while also changing the trade-off between overall accuracy and class-level performance.

The Random Forest model is the best model so far for balanced class performance, especially draw prediction, but the overall model is still weak and should not be treated as a final strong predictor.

Current Stratified K-Fold Random Forest result:

```text
Accuracy:        0.497
Macro F1:        0.473
Weighted F1:     0.499
Draw precision:  0.313
Draw recall:     0.363
Draw F1 score:   0.333
```

Random Forest was also tuned with GridSearchCV using macro F1 as the main optimization metric.

Best GridSearchCV parameters:

```text
class_weight:     balanced
max_depth:        4
max_features:     sqrt
min_samples_leaf: 5
n_estimators:     200
```

Tuned Random Forest result:

```text
Accuracy:        0.497
Macro F1:        0.476
Weighted F1:     0.501
Draw precision:  0.303
Draw recall:     0.399
Draw F1 score:   0.342
```

GridSearchCV produced only marginal gains. It improved draw recall and draw F1 slightly, but it did not materially improve the overall model. This suggests the current limitation is likely the small dataset and available features, not only Random Forest hyperparameters.

MLflow is used to track model runs, metrics, parameters, artifacts, and trained model outputs locally.

The main comparison metrics are:

```text
accuracy
macro F1 score
weighted F1 score
draw precision
draw recall
draw F1 score
```

More detailed ML documentation is available in:

```text
ml/README.md
```

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

## ✅ CI, Automation, and Repository Cleanup

The project includes two GitHub Actions workflows:

```text
.github/workflows/ci.yml
.github/workflows/full_pipeline.yml
```

The CI workflow runs on pull requests and pushes to `main`.

It checks that:

* Python dependencies can be installed
* Python files in `ingestion/` and `ml/` have valid syntax
* the dbt project can be parsed successfully

This is a lightweight safety check. It does not run the full data pipeline, load BigQuery data, run dbt models, or train ML models.

The full pipeline workflow can be run manually from GitHub Actions and is also scheduled to run daily.

It runs:

```text
fetch API data
-> prepare JSONL
-> load raw fixtures to BigQuery
-> run dbt models
-> run dbt tests
```

The full pipeline workflow requires GitHub repository secrets for the football API key and Google Cloud authentication.

Generated local artifacts are ignored by Git so the repository stays clean.

Ignored local outputs include:

```text
data/raw/*.json
data/raw/*.jsonl
dbt_project/logs/
dbt_project/target/
mlruns/
mlartifacts/
mlflow.db
reports/
```

These files can be recreated locally and should not usually be committed.

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
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── full_pipeline.yml
│
├── ingestion/
│   ├── fetch_data.py
│   ├── prepare_bigquery_jsonl.py
│   └── load_bigquery.py
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
├── ml/
│   ├── README.md
│   ├── evaluate_stratified_k_fold.py
│   ├── train_baseline_model.py
│   ├── train_balanced_logistic_regression.py
│   ├── train_random_forest_model.py
│   └── tune_random_forest_grid_search.py
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
* baseline machine learning model training
* MLflow experiment tracking
* Stratified K-Fold model evaluation
* Random Forest model comparison
* Random Forest hyperparameter tuning with GridSearchCV
* basic GitHub Actions CI checks
* scheduled GitHub Actions pipeline automation
* repository cleanup with generated files ignored by Git
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
* Logistic Regression baseline model created in Python
* baseline model evaluated against a majority-class guess
* balanced Logistic Regression model added to improve draw prediction handling
* MLflow tracking added for local model experiment tracking
* Stratified K-Fold cross-validation evaluation added
* Random Forest comparison model added
* Random Forest GridSearchCV tuning added
* Power BI dashboard created for Premier League 2023/24 season overview
* Power BI KPI cards updated to use the `season_summary` dbt mart table
* dashboard screenshot added to the repository and README
* basic GitHub Actions CI workflow added
* full pipeline GitHub Actions workflow added
* BigQuery raw data load script added
* generated local artifacts ignored with `.gitignore`

Current focus:

* interpret model results honestly and avoid overclaiming model strength
* keep the repository clean and easy to review
* document the project clearly as a portfolio project
* monitor scheduled pipeline runs in GitHub Actions

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
* [x] Train baseline model
* [x] Evaluate baseline model performance
* [x] Improve draw prediction handling with balanced Logistic Regression
* [x] Track model results with MLflow
* [x] Compare model results with cross-validation
* [x] Add Random Forest comparison model
* [x] Tune Random Forest with GridSearchCV
* [x] Document initial ML findings

---

### Phase 7: Automation

* [x] Add basic GitHub Actions workflow
* [x] Check Python syntax in CI
* [x] Check dbt project parsing in CI
* [x] Add full pipeline GitHub Actions workflow
* [x] Automate data ingestion
* [x] Automate raw data loading to BigQuery
* [x] Automate dbt transformations
* [x] Automate dbt validation tests

---

## ▶️ How to Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run lightweight local checks:

```bash
python -m compileall -q ingestion ml
cd dbt_project
dbt parse
cd ..
```

Run the data ingestion script:

```bash
python ingestion/fetch_data.py
```

Prepare the JSONL file for BigQuery:

```bash
python ingestion/prepare_bigquery_jsonl.py
```

Load the raw fixture data to BigQuery:

```bash
python ingestion/load_bigquery.py
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

Run the baseline ML model:

```bash
python ml/train_baseline_model.py
```

Run the balanced Logistic Regression model:

```bash
python ml/train_balanced_logistic_regression.py
```

Run the Random Forest model:

```bash
python ml/train_random_forest_model.py
```

Run Stratified K-Fold model comparison:

```bash
python ml/evaluate_stratified_k_fold.py
```

Tune the Random Forest model with GridSearchCV:

```bash
python ml/tune_random_forest_grid_search.py
```

Start the local MLflow UI:

```bash
python -m mlflow ui --backend-store-uri sqlite:///mlflow.db
```

---

## 🔐 Environment Variables

API keys should not be written directly in the code.

The local ingestion script uses this environment variable:

```text
FOOTBALL_API_KEY
```

This keeps sensitive keys outside the source code.

Example `.env` file:

```text
FOOTBALL_API_KEY=your_api_key_here
```

The `.env` file is ignored by Git and should not be pushed to GitHub.

The BigQuery load script also supports these optional environment variables:

```text
GCP_PROJECT_ID
BIGQUERY_RAW_DATASET
BIGQUERY_RAW_TABLE
BIGQUERY_FIXTURES_JSONL
```

If these are not set, the script uses the project defaults:

```text
GCP_PROJECT_ID=football-analytics-ml
BIGQUERY_RAW_DATASET=football_raw
BIGQUERY_RAW_TABLE=raw_fixtures
BIGQUERY_FIXTURES_JSONL=data/raw/fixtures_premier_league_2023_rows.jsonl
```

The full GitHub Actions pipeline requires these repository secrets:

```text
FOOTBALL_API_KEY
GCP_SERVICE_ACCOUNT_KEY
```

`GCP_SERVICE_ACCOUNT_KEY` should contain a Google Cloud service account JSON key with permission to create/load the raw BigQuery table and run dbt models in BigQuery.

---

## 📌 Notes

This project is portfolio-ready as an end-to-end analytics and introductory ML pipeline.

The current version focuses on:

```text
API data collection
→ raw data storage
→ BigQuery loading
→ dbt transformation
→ data quality testing
→ dashboard-ready tables
→ Power BI dashboard
→ ML-ready feature table
→ model comparison and MLflow tracking
→ basic CI checks
→ scheduled full pipeline automation
```

The dashboard KPI logic is prepared in dbt using the `season_summary` mart table, while Power BI is used mainly for visualization.

The machine learning layer has a documented feature mart, a prediction target, season-to-date features, recent-form features, an original Logistic Regression baseline model, a balanced Logistic Regression model, a Random Forest comparison model, Stratified K-Fold evaluation, Random Forest GridSearchCV tuning, and local MLflow experiment tracking. Random Forest currently gives the best balanced class performance, but GridSearchCV only produced marginal gains and the overall model is still weak.

The ML results should be presented honestly as an experiment and evaluation workflow, not as a strong final prediction system. If the project is extended later, the most useful next improvements would likely come from more seasons of data and better pre-match features.

Generated files such as raw API extracts, dbt build artifacts, MLflow runs, local reports, virtual environments, and local editor files are ignored by Git so the repository stays clean.

---

## 👤 Author

Created by **Ibne Sina Khan**

This project is part of a portfolio focused on data analytics, cloud data pipelines, automation, and machine learning.
