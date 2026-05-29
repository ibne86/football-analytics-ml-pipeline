<div align="center">

# ⚽ Football Analytics & ML Pipeline

**End-to-end football data pipeline for data collection, cloud storage, SQL transformation, analytics dashboards, and machine learning-based match prediction.**

<br>

![Python](https://img.shields.io/badge/PYTHON-3776AB?style=for-the-badge&logo=python&logoColor=white)
![BigQuery](https://img.shields.io/badge/BIGQUERY-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)
![dbt](https://img.shields.io/badge/DBT-FF694B?style=for-the-badge&logo=dbt&logoColor=white)
![Power BI](https://img.shields.io/badge/POWER%20BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Machine Learning](https://img.shields.io/badge/MACHINE%20LEARNING-102230?style=for-the-badge)
![GitHub Actions](https://img.shields.io/badge/GITHUB%20ACTIONS-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

</div>

---

## 📌 Project Overview

This project is an end-to-end football analytics and machine learning pipeline.

The goal is to collect football match data from an API, store the raw data in BigQuery, transform it using dbt, create clean analytics tables, build Power BI dashboards, and use the prepared data for machine learning-based match prediction.

---

## 🏗️ Pipeline Architecture

```text
Football API
    ↓
Python Data Ingestion
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