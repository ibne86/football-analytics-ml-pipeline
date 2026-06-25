from __future__ import annotations

import json
import os
from tempfile import TemporaryDirectory

import mlflow
import mlflow.sklearn
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from train_baseline_model import (
    DEFAULT_FEATURE_TABLE,
    DEFAULT_MLFLOW_EXPERIMENT,
    DEFAULT_MLFLOW_TRACKING_URI,
    OUTCOME_REFERENCE_COLUMNS,
    RANDOM_STATE,
    SAFE_FEATURE_COLUMNS,
    TARGET_COLUMN,
    TEST_SIZE,
    load_feature_data,
    metric_name,
    validate_input_data,
    value_counts_dict,
)


MODEL_NAME = "random_forest_classifier"
CLASS_WEIGHT = "balanced"
N_ESTIMATORS = 200
MAX_DEPTH = 4
MIN_SAMPLES_LEAF = 10


def build_random_forest_model() -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=N_ESTIMATORS,
                    max_depth=MAX_DEPTH,
                    min_samples_leaf=MIN_SAMPLES_LEAF,
                    class_weight=CLASS_WEIGHT,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def log_mlflow_run(
    model: Pipeline,
    table_id: str,
    df: pd.DataFrame,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    predictions: list[str],
    labels: list[str],
    majority_class: str,
    majority_accuracy: float,
    model_accuracy: float,
) -> None:
    classification_report_dict = classification_report(
        y_test,
        predictions,
        labels=labels,
        zero_division=0,
        output_dict=True,
    )
    confusion_matrix_df = pd.DataFrame(
        confusion_matrix(y_test, predictions, labels=labels),
        index=labels,
        columns=labels,
    )

    with mlflow.start_run(run_name=MODEL_NAME) as run:
        mlflow.log_params(
            {
                "model_name": MODEL_NAME,
                "model_type": "RandomForestClassifier",
                "class_weight": CLASS_WEIGHT,
                "n_estimators": N_ESTIMATORS,
                "max_depth": MAX_DEPTH,
                "min_samples_leaf": MIN_SAMPLES_LEAF,
                "feature_table": table_id,
                "target_column": TARGET_COLUMN,
                "test_size": TEST_SIZE,
                "random_state": RANDOM_STATE,
                "rows_loaded": len(df),
                "training_rows": len(X_train),
                "test_rows": len(X_test),
                "input_feature_count": len(SAFE_FEATURE_COLUMNS),
                "majority_class": majority_class,
            }
        )

        mlflow.log_metrics(
            {
                "majority_class_accuracy": majority_accuracy,
                "model_accuracy": model_accuracy,
            }
        )

        for label in labels:
            label_report = classification_report_dict[label]
            mlflow.log_metrics(
                {
                    metric_name(label, "precision"): label_report["precision"],
                    metric_name(label, "recall"): label_report["recall"],
                    metric_name(label, "f1_score"): label_report["f1-score"],
                    metric_name(label, "support"): label_report["support"],
                }
            )

        for label in ["macro avg", "weighted avg"]:
            label_report = classification_report_dict[label]
            mlflow.log_metrics(
                {
                    metric_name(label, "precision"): label_report["precision"],
                    metric_name(label, "recall"): label_report["recall"],
                    metric_name(label, "f1_score"): label_report["f1-score"],
                }
            )

        mlflow.log_dict(
            {
                "input_features": SAFE_FEATURE_COLUMNS,
                "excluded_outcome_reference_columns": OUTCOME_REFERENCE_COLUMNS,
                "target_distribution": value_counts_dict(df[TARGET_COLUMN]),
                "train_target_distribution": value_counts_dict(y_train),
                "test_target_distribution": value_counts_dict(y_test),
            },
            "run_metadata.json",
        )

        with TemporaryDirectory() as temp_dir:
            classification_report_path = os.path.join(temp_dir, "classification_report.json")
            confusion_matrix_path = os.path.join(temp_dir, "confusion_matrix.csv")

            with open(classification_report_path, "w", encoding="utf-8") as file:
                json.dump(classification_report_dict, file, indent=2)

            confusion_matrix_df.to_csv(confusion_matrix_path)

            mlflow.log_artifact(classification_report_path, artifact_path="evaluation")
            mlflow.log_artifact(confusion_matrix_path, artifact_path="evaluation")

        mlflow.sklearn.log_model(
            model,
            name="model",
            serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE,
        )

        print()
        print("MLflow run logged:")
        print(f"- run_id: {run.info.run_id}")


def train_random_forest_model(df: pd.DataFrame, table_id: str) -> None:
    X = df[SAFE_FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    class_counts = y.value_counts()
    stratify_target = y if class_counts.min() >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=stratify_target,
    )

    model = build_random_forest_model()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    model_accuracy = accuracy_score(y_test, predictions)

    majority_class = y_train.mode()[0]
    majority_predictions = [majority_class] * len(y_test)
    majority_accuracy = accuracy_score(y_test, majority_predictions)

    labels = sorted(y.unique())

    print("Model: Random Forest Classifier")
    print(f"Feature table: {table_id}")
    print(f"Rows loaded: {len(df)}")
    print(f"Training rows: {len(X_train)}")
    print(f"Test rows: {len(X_test)}")
    print()
    print("Model settings:")
    print(f"- class_weight: {CLASS_WEIGHT}")
    print(f"- n_estimators: {N_ESTIMATORS}")
    print(f"- max_depth: {MAX_DEPTH}")
    print(f"- min_samples_leaf: {MIN_SAMPLES_LEAF}")
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
    print(f"Random Forest accuracy: {model_accuracy:.3f}")
    print()
    print("Classification report:")
    print(classification_report(y_test, predictions, labels=labels, zero_division=0))
    print("Confusion matrix:")
    print(pd.DataFrame(confusion_matrix(y_test, predictions, labels=labels), index=labels, columns=labels))

    log_mlflow_run(
        model=model,
        table_id=table_id,
        df=df,
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        predictions=predictions,
        labels=labels,
        majority_class=majority_class,
        majority_accuracy=majority_accuracy,
        model_accuracy=model_accuracy,
    )


def main() -> None:
    load_dotenv()

    feature_table = os.getenv("ML_FEATURE_TABLE", DEFAULT_FEATURE_TABLE)
    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", DEFAULT_MLFLOW_TRACKING_URI)
    mlflow_experiment = os.getenv("MLFLOW_EXPERIMENT_NAME", DEFAULT_MLFLOW_EXPERIMENT)

    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(mlflow_experiment)

    df = load_feature_data(feature_table)
    validate_input_data(df)
    train_random_forest_model(df, feature_table)


if __name__ == "__main__":
    main()
