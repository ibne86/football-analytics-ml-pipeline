from __future__ import annotations

import json
import os
from tempfile import TemporaryDirectory

import mlflow
import pandas as pd
from dotenv import load_dotenv
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from train_baseline_model import (
    DEFAULT_FEATURE_TABLE,
    DEFAULT_MLFLOW_EXPERIMENT,
    DEFAULT_MLFLOW_TRACKING_URI,
    OUTCOME_REFERENCE_COLUMNS,
    RANDOM_STATE,
    SAFE_FEATURE_COLUMNS,
    TARGET_COLUMN,
    load_feature_data,
    validate_input_data,
    value_counts_dict,
)


CV_SPLITS = 5
DRAW_LABEL = "Draw"

METRIC_COLUMNS = [
    "majority_class_accuracy",
    "accuracy",
    "macro_f1",
    "weighted_f1",
    "draw_precision",
    "draw_recall",
    "draw_f1_score",
]

MODEL_CONFIGS = [
    {
        "model_name": "baseline_logistic_regression_stratified_k_fold",
        "display_name": "Baseline Logistic Regression",
        "class_weight": None,
    },
    {
        "model_name": "balanced_logistic_regression_stratified_k_fold",
        "display_name": "Balanced Logistic Regression",
        "class_weight": "balanced",
    },
]


def build_model(class_weight: str | None) -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(max_iter=1000, class_weight=class_weight),
            ),
        ]
    )


def validate_cv_split_count(y: pd.Series) -> None:
    smallest_class_count = y.value_counts().min()

    if smallest_class_count < CV_SPLITS:
        raise ValueError(
            f"Cannot run {CV_SPLITS}-fold cross-validation because the smallest "
            f"class has only {smallest_class_count} rows."
        )


def calculate_metrics(
    y_true: pd.Series,
    predictions: list[str] | pd.Series,
    labels: list[str],
    majority_predictions: list[str] | None = None,
) -> dict[str, float]:
    report = classification_report(
        y_true,
        predictions,
        labels=labels,
        zero_division=0,
        output_dict=True,
    )
    draw_report = report[DRAW_LABEL]

    metrics = {
        "accuracy": accuracy_score(y_true, predictions),
        "macro_f1": report["macro avg"]["f1-score"],
        "weighted_f1": report["weighted avg"]["f1-score"],
        "draw_precision": draw_report["precision"],
        "draw_recall": draw_report["recall"],
        "draw_f1_score": draw_report["f1-score"],
    }

    if majority_predictions is not None:
        metrics["majority_class_accuracy"] = accuracy_score(y_true, majority_predictions)

    return metrics


def summarize_fold_metrics(
    model_config: dict[str, str | None],
    fold_metrics_df: pd.DataFrame,
) -> dict[str, str | float]:
    summary: dict[str, str | float] = {
        "model_name": str(model_config["model_name"]),
        "display_name": str(model_config["display_name"]),
        "class_weight": str(model_config["class_weight"] or "none"),
    }

    for metric in METRIC_COLUMNS:
        summary[f"{metric}_mean"] = fold_metrics_df[metric].mean()
        summary[f"{metric}_std"] = fold_metrics_df[metric].std(ddof=0)

    return summary


def log_cv_run(
    model_config: dict[str, str | None],
    table_id: str,
    df: pd.DataFrame,
    labels: list[str],
    fold_metrics_df: pd.DataFrame,
    summary: dict[str, str | float],
    overall_report: dict[str, dict[str, float]],
    overall_confusion_matrix_df: pd.DataFrame,
) -> None:
    with mlflow.start_run(run_name=str(model_config["model_name"])) as run:
        mlflow.log_params(
            {
                "model_name": model_config["model_name"],
                "model_type": "LogisticRegression",
                "class_weight": model_config["class_weight"] or "none",
                "feature_table": table_id,
                "target_column": TARGET_COLUMN,
                "cv_strategy": "StratifiedKFold",
                "cv_splits": CV_SPLITS,
                "cv_shuffle": True,
                "random_state": RANDOM_STATE,
                "rows_loaded": len(df),
                "input_feature_count": len(SAFE_FEATURE_COLUMNS),
            }
        )

        for metric in METRIC_COLUMNS:
            mlflow.log_metric(f"{metric}_mean", float(summary[f"{metric}_mean"]))
            mlflow.log_metric(f"{metric}_std", float(summary[f"{metric}_std"]))

            for fold_number, metric_value in enumerate(fold_metrics_df[metric], start=1):
                mlflow.log_metric(f"{metric}_fold", float(metric_value), step=fold_number)

        mlflow.log_dict(
            {
                "input_features": SAFE_FEATURE_COLUMNS,
                "excluded_outcome_reference_columns": OUTCOME_REFERENCE_COLUMNS,
                "target_distribution": value_counts_dict(df[TARGET_COLUMN]),
            },
            "run_metadata.json",
        )

        with TemporaryDirectory() as temp_dir:
            fold_metrics_path = os.path.join(temp_dir, "fold_metrics.csv")
            classification_report_path = os.path.join(
                temp_dir,
                "out_of_fold_classification_report.json",
            )
            confusion_matrix_path = os.path.join(
                temp_dir,
                "out_of_fold_confusion_matrix.csv",
            )

            fold_metrics_df.to_csv(fold_metrics_path, index=False)

            with open(classification_report_path, "w", encoding="utf-8") as file:
                json.dump(overall_report, file, indent=2)

            overall_confusion_matrix_df.to_csv(confusion_matrix_path)

            mlflow.log_artifact(fold_metrics_path, artifact_path="cross_validation")
            mlflow.log_artifact(
                classification_report_path,
                artifact_path="cross_validation",
            )
            mlflow.log_artifact(confusion_matrix_path, artifact_path="cross_validation")

        print(f"MLflow CV run logged for {model_config['display_name']}:")
        print(f"- run_id: {run.info.run_id}")


def evaluate_model_with_stratified_k_fold(
    model_config: dict[str, str | None],
    table_id: str,
    df: pd.DataFrame,
    cv: StratifiedKFold,
    labels: list[str],
) -> dict[str, str | float]:
    X = df[SAFE_FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    fold_rows = []
    out_of_fold_predictions = pd.Series(index=y.index, dtype="object")

    for fold_number, (train_index, test_index) in enumerate(cv.split(X, y), start=1):
        X_train = X.iloc[train_index]
        X_test = X.iloc[test_index]
        y_train = y.iloc[train_index]
        y_test = y.iloc[test_index]

        model = build_model(model_config["class_weight"])
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        out_of_fold_predictions.iloc[test_index] = predictions

        majority_class = y_train.mode()[0]
        majority_predictions = [majority_class] * len(y_test)

        fold_metrics = calculate_metrics(
            y_true=y_test,
            predictions=predictions,
            labels=labels,
            majority_predictions=majority_predictions,
        )

        fold_rows.append(
            {
                "model_name": model_config["model_name"],
                "fold": fold_number,
                "training_rows": len(X_train),
                "test_rows": len(X_test),
                "majority_class": majority_class,
                **fold_metrics,
            }
        )

    fold_metrics_df = pd.DataFrame(fold_rows)
    summary = summarize_fold_metrics(model_config, fold_metrics_df)

    overall_report = classification_report(
        y,
        out_of_fold_predictions,
        labels=labels,
        zero_division=0,
        output_dict=True,
    )
    overall_confusion_matrix_df = pd.DataFrame(
        confusion_matrix(y, out_of_fold_predictions, labels=labels),
        index=labels,
        columns=labels,
    )

    log_cv_run(
        model_config=model_config,
        table_id=table_id,
        df=df,
        labels=labels,
        fold_metrics_df=fold_metrics_df,
        summary=summary,
        overall_report=overall_report,
        overall_confusion_matrix_df=overall_confusion_matrix_df,
    )

    return summary


def format_summary_for_print(summary_df: pd.DataFrame) -> pd.DataFrame:
    display_rows = []

    for _, row in summary_df.iterrows():
        display_row = {
            "model": row["display_name"],
            "class_weight": row["class_weight"],
        }

        for metric in METRIC_COLUMNS:
            display_row[metric] = (
                f"{row[f'{metric}_mean']:.3f} "
                f"(+/- {row[f'{metric}_std']:.3f})"
            )

        display_rows.append(display_row)

    return pd.DataFrame(display_rows)


def run_stratified_k_fold_evaluation(df: pd.DataFrame, table_id: str) -> None:
    y = df[TARGET_COLUMN]
    labels = sorted(y.unique())

    if DRAW_LABEL not in labels:
        raise ValueError(f"Expected target label '{DRAW_LABEL}' was not found.")

    validate_cv_split_count(y)

    cv = StratifiedKFold(
        n_splits=CV_SPLITS,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    print("Stratified K-Fold evaluation")
    print(f"Feature table: {table_id}")
    print(f"Rows loaded: {len(df)}")
    print(f"Number of folds: {CV_SPLITS}")
    print()
    print("Target distribution:")
    for label, count in value_counts_dict(y).items():
        print(f"- {label}: {count}")
    print()

    summaries = []
    for model_config in MODEL_CONFIGS:
        print(f"Evaluating: {model_config['display_name']}")
        summaries.append(
            evaluate_model_with_stratified_k_fold(
                model_config=model_config,
                table_id=table_id,
                df=df,
                cv=cv,
                labels=labels,
            )
        )
        print()

    summary_df = pd.DataFrame(summaries)

    print("Cross-validation summary:")
    print(format_summary_for_print(summary_df).to_string(index=False))


def main() -> None:
    load_dotenv()

    feature_table = os.getenv("ML_FEATURE_TABLE", DEFAULT_FEATURE_TABLE)
    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", DEFAULT_MLFLOW_TRACKING_URI)
    mlflow_experiment = os.getenv("MLFLOW_EXPERIMENT_NAME", DEFAULT_MLFLOW_EXPERIMENT)

    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(mlflow_experiment)

    df = load_feature_data(feature_table)
    validate_input_data(df)
    run_stratified_k_fold_evaluation(df, feature_table)


if __name__ == "__main__":
    main()
