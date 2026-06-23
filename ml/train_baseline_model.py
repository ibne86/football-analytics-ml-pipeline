from __future__ import annotations

import os

import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


DEFAULT_FEATURE_TABLE = "football-analytics-ml.football_dbt.ml_match_features"
TARGET_COLUMN = "target_match_result"

SAFE_FEATURE_COLUMNS = [
    "home_matches_played_before",
    "away_matches_played_before",
    "home_points_before",
    "away_points_before",
    "home_avg_points_before",
    "away_avg_points_before",
    "home_points_last_5",
    "away_points_last_5",
    "home_avg_points_last_5",
    "away_avg_points_last_5",
    "home_goals_for_last_5",
    "away_goals_for_last_5",
    "home_goals_against_last_5",
    "away_goals_against_last_5",
]

OUTCOME_REFERENCE_COLUMNS = [
    "home_goals",
    "away_goals",
    "total_goals",
    "match_result",
    "target_match_result",
    "is_home_win",
    "is_away_win",
    "is_draw",
]


def quote_table_id(table_id: str) -> str:
    if "`" in table_id:
        raise ValueError("ML_FEATURE_TABLE must not contain backticks.")

    return f"`{table_id}`"


def load_feature_data(table_id: str) -> pd.DataFrame:
    selected_columns = ["match_id", "match_date", TARGET_COLUMN, *SAFE_FEATURE_COLUMNS]
    selected_sql = ",\n        ".join(selected_columns)

    query = f"""
    select
        {selected_sql}
    from {quote_table_id(table_id)}
    where {TARGET_COLUMN} is not null
    order by match_date, match_id
    """

    client = bigquery.Client()
    return client.query(query).to_dataframe()


def validate_input_data(df: pd.DataFrame) -> None:
    missing_columns = [
        column
        for column in [TARGET_COLUMN, *SAFE_FEATURE_COLUMNS]
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    if df.empty:
        raise ValueError("No rows returned from the ML feature table.")

    class_count = df[TARGET_COLUMN].nunique()
    if class_count < 2:
        raise ValueError("The target column must contain at least two classes.")


def train_baseline_model(df: pd.DataFrame, table_id: str) -> None:
    X = df[SAFE_FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    class_counts = y.value_counts()
    stratify_target = y if class_counts.min() >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=stratify_target,
    )

    model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    model_accuracy = accuracy_score(y_test, predictions)

    majority_class = y_train.mode()[0]
    majority_predictions = [majority_class] * len(y_test)
    majority_accuracy = accuracy_score(y_test, majority_predictions)

    labels = sorted(y.unique())

    print("Baseline model: Logistic Regression")
    print(f"Feature table: {table_id}")
    print(f"Rows loaded: {len(df)}")
    print(f"Training rows: {len(X_train)}")
    print(f"Test rows: {len(X_test)}")
    print()
    print("Input features used:")
    for column in SAFE_FEATURE_COLUMNS:
        print(f"- {column}")
    print()
    print("Outcome/reference columns intentionally excluded from input features:")
    for column in OUTCOME_REFERENCE_COLUMNS:
        print(f"- {column}")
    print()
    print(f"Majority-class guess: {majority_class}")
    print(f"Majority-class accuracy: {majority_accuracy:.3f}")
    print(f"Logistic Regression accuracy: {model_accuracy:.3f}")
    print()
    print("Classification report:")
    print(classification_report(y_test, predictions, labels=labels, zero_division=0))
    print("Confusion matrix:")
    print(pd.DataFrame(confusion_matrix(y_test, predictions, labels=labels), index=labels, columns=labels))


def main() -> None:
    load_dotenv()

    feature_table = os.getenv("ML_FEATURE_TABLE", DEFAULT_FEATURE_TABLE)

    df = load_feature_data(feature_table)
    validate_input_data(df)
    train_baseline_model(df, feature_table)


if __name__ == "__main__":
    main()
