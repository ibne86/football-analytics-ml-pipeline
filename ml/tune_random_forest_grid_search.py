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
from sklearn.metrics import f1_score, make_scorer, precision_score, recall_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline

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


MODEL_NAME = "random_forest_grid_search_cv"
CV_SPLITS = 5
REFIT_METRIC = "macro_f1"
DRAW_LABEL = "Draw"

PARAM_GRID = {
    "classifier__n_estimators": [100, 200],
    "classifier__max_depth": [3, 4, 5],
    "classifier__min_samples_leaf": [5, 10, 15],
    "classifier__max_features": ["sqrt"],
    "classifier__class_weight": ["balanced", "balanced_subsample"],
}

SCORING = {
    "accuracy": "accuracy",
    "balanced_accuracy": "balanced_accuracy",
    "macro_f1": make_scorer(f1_score, average="macro", zero_division=0),
    "weighted_f1": make_scorer(f1_score, average="weighted", zero_division=0),
    "draw_precision": make_scorer(
        precision_score,
        labels=[DRAW_LABEL],
        average="macro",
        zero_division=0,
    ),
    "draw_recall": make_scorer(
        recall_score,
        labels=[DRAW_LABEL],
        average="macro",
        zero_division=0,
    ),
    "draw_f1_score": make_scorer(
        f1_score,
        labels=[DRAW_LABEL],
        average="macro",
        zero_division=0,
    ),
}


def build_random_forest_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("classifier", RandomForestClassifier(random_state=RANDOM_STATE)),
        ]
    )


def validate_grid_search_inputs(y: pd.Series) -> None:
    smallest_class_count = y.value_counts().min()

    if DRAW_LABEL not in set(y):
        raise ValueError(f"Expected target label '{DRAW_LABEL}' was not found.")

    if smallest_class_count < CV_SPLITS:
        raise ValueError(
            f"Cannot run {CV_SPLITS}-fold GridSearchCV because the smallest "
            f"class has only {smallest_class_count} rows."
        )


def remove_pipeline_prefix(params: dict[str, object]) -> dict[str, object]:
    return {
        key.replace("classifier__", ""): value
        for key, value in params.items()
    }


def get_best_metric_summary(cv_results_df: pd.DataFrame, best_index: int) -> dict[str, float]:
    summary = {}

    for metric_name in SCORING:
        summary[f"{metric_name}_mean"] = float(
            cv_results_df.loc[best_index, f"mean_test_{metric_name}"]
        )
        summary[f"{metric_name}_std"] = float(
            cv_results_df.loc[best_index, f"std_test_{metric_name}"]
        )

    return summary


def print_grid_search_summary(
    grid_search: GridSearchCV,
    cv_results_df: pd.DataFrame,
    best_metric_summary: dict[str, float],
) -> None:
    best_params = remove_pipeline_prefix(grid_search.best_params_)

    print("Random Forest GridSearchCV")
    print(f"Best score metric: {REFIT_METRIC}")
    print(f"Best {REFIT_METRIC}: {grid_search.best_score_:.3f}")
    print()
    print("Best parameters:")
    for key, value in best_params.items():
        print(f"- {key}: {value}")
    print()
    print("Best model cross-validation metrics:")
    for metric_name in SCORING:
        print(
            f"- {metric_name}: "
            f"{best_metric_summary[f'{metric_name}_mean']:.3f} "
            f"(+/- {best_metric_summary[f'{metric_name}_std']:.3f})"
        )
    print()

    display_columns = [
        "rank_test_macro_f1",
        "mean_test_macro_f1",
        "std_test_macro_f1",
        "mean_test_accuracy",
        "mean_test_draw_f1_score",
        "param_classifier__n_estimators",
        "param_classifier__max_depth",
        "param_classifier__min_samples_leaf",
        "param_classifier__class_weight",
    ]

    print("Top parameter combinations:")
    print(
        cv_results_df[display_columns]
        .sort_values("rank_test_macro_f1")
        .head(10)
        .to_string(index=False)
    )


def log_grid_search_run(
    grid_search: GridSearchCV,
    table_id: str,
    df: pd.DataFrame,
    cv_results_df: pd.DataFrame,
    best_metric_summary: dict[str, float],
    param_grid: dict[str, list[object]],
) -> None:
    best_params = remove_pipeline_prefix(grid_search.best_params_)

    with mlflow.start_run(run_name=MODEL_NAME) as run:
        mlflow.log_params(
            {
                "model_name": MODEL_NAME,
                "model_type": "RandomForestClassifier",
                "tuning_method": "GridSearchCV",
                "refit_metric": REFIT_METRIC,
                "cv_strategy": "StratifiedKFold",
                "cv_splits": CV_SPLITS,
                "cv_shuffle": True,
                "random_state": RANDOM_STATE,
                "feature_table": table_id,
                "target_column": TARGET_COLUMN,
                "rows_loaded": len(df),
                "input_feature_count": len(SAFE_FEATURE_COLUMNS),
                "candidate_count": len(cv_results_df),
            }
        )
        mlflow.log_params({f"best_{key}": value for key, value in best_params.items()})

        for metric_name in SCORING:
            mlflow.log_metric(
                f"{metric_name}_mean",
                best_metric_summary[f"{metric_name}_mean"],
            )
            mlflow.log_metric(
                f"{metric_name}_std",
                best_metric_summary[f"{metric_name}_std"],
            )

        mlflow.log_dict(
            {
                "param_grid": param_grid,
                "best_params": best_params,
                "input_features": SAFE_FEATURE_COLUMNS,
                "excluded_outcome_reference_columns": OUTCOME_REFERENCE_COLUMNS,
                "target_distribution": value_counts_dict(df[TARGET_COLUMN]),
            },
            "grid_search_metadata.json",
        )

        with TemporaryDirectory() as temp_dir:
            cv_results_path = os.path.join(temp_dir, "grid_search_cv_results.csv")
            best_params_path = os.path.join(temp_dir, "best_params.json")

            cv_results_df.to_csv(cv_results_path, index=False)

            with open(best_params_path, "w", encoding="utf-8") as file:
                json.dump(best_params, file, indent=2)

            mlflow.log_artifact(cv_results_path, artifact_path="grid_search")
            mlflow.log_artifact(best_params_path, artifact_path="grid_search")

        mlflow.sklearn.log_model(
            grid_search.best_estimator_,
            name="model",
            serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE,
        )

        print()
        print("MLflow GridSearchCV run logged:")
        print(f"- run_id: {run.info.run_id}")


def run_random_forest_grid_search(
    df: pd.DataFrame,
    table_id: str,
    param_grid: dict[str, list[object]] | None = None,
) -> None:
    selected_param_grid = param_grid or PARAM_GRID
    X = df[SAFE_FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    validate_grid_search_inputs(y)

    cv = StratifiedKFold(
        n_splits=CV_SPLITS,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    grid_search = GridSearchCV(
        estimator=build_random_forest_pipeline(),
        param_grid=selected_param_grid,
        scoring=SCORING,
        refit=REFIT_METRIC,
        cv=cv,
        n_jobs=1,
        return_train_score=True,
    )
    grid_search.fit(X, y)

    cv_results_df = pd.DataFrame(grid_search.cv_results_)
    best_metric_summary = get_best_metric_summary(
        cv_results_df=cv_results_df,
        best_index=grid_search.best_index_,
    )

    print_grid_search_summary(
        grid_search=grid_search,
        cv_results_df=cv_results_df,
        best_metric_summary=best_metric_summary,
    )
    log_grid_search_run(
        grid_search=grid_search,
        table_id=table_id,
        df=df,
        cv_results_df=cv_results_df,
        best_metric_summary=best_metric_summary,
        param_grid=selected_param_grid,
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
    run_random_forest_grid_search(df, feature_table)


if __name__ == "__main__":
    main()
