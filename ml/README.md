# Machine Learning

This folder contains the machine learning part of the football analytics pipeline.

The goal is to predict:

```text
target_match_result = Home Win / Draw / Away Win
```

The models use leakage-safe pre-match features from the dbt mart:

```text
football_dbt.ml_match_features
```

Outcome columns such as goals, match result, and win/draw flags are kept as reference columns, but they are not used as model inputs.

## Scripts

| Script | Purpose |
| --- | --- |
| `train_baseline_model.py` | Trains the original Logistic Regression baseline. |
| `train_balanced_logistic_regression.py` | Trains Logistic Regression with balanced class weights. |
| `train_random_forest_model.py` | Trains the current best comparison model, Random Forest. |
| `evaluate_stratified_k_fold.py` | Compares models with Stratified K-Fold cross-validation. |
| `tune_random_forest_grid_search.py` | Tunes Random Forest with GridSearchCV using macro F1. |

## Current Model Results

The current best model is Random Forest when judged by balanced class performance.

| Model | Accuracy | Macro F1 | Weighted F1 | Draw F1 | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| Baseline Logistic Regression | 0.537 | 0.394 | 0.471 | 0.000 | Good accuracy, but ignored draws. |
| Balanced Logistic Regression | 0.434 | 0.396 | 0.437 | 0.175 | Improved draw prediction, lower accuracy. |
| Random Forest | 0.497 | 0.473 | 0.499 | 0.333 | Best balanced class performance so far. |
| Tuned Random Forest | 0.497 | 0.476 | 0.501 | 0.342 | Only marginally better than Random Forest. |

The tuned Random Forest used:

```text
class_weight:     balanced
max_depth:        4
max_features:     sqrt
min_samples_leaf: 5
n_estimators:     200
```

## Metrics

Accuracy is useful, but it is not enough for this project.

The dataset has three classes:

```text
Home Win
Draw
Away Win
```

The original Logistic Regression model had reasonable accuracy, but it never predicted Draw. Because of that, the main metric is:

```text
macro F1
```

Macro F1 gives each class equal importance. This makes it harder for the model to look good by only predicting the most common class.

Important supporting metrics:

```text
accuracy
weighted F1
draw precision
draw recall
draw F1
```

## How To Run

Run the original baseline:

```bash
python ml/train_baseline_model.py
```

Run balanced Logistic Regression:

```bash
python ml/train_balanced_logistic_regression.py
```

Run Random Forest:

```bash
python ml/train_random_forest_model.py
```

Compare models with Stratified K-Fold:

```bash
python ml/evaluate_stratified_k_fold.py
```

Tune Random Forest:

```bash
python ml/tune_random_forest_grid_search.py
```

Start the local MLflow UI:

```bash
python -m mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Then open:

```text
http://127.0.0.1:5000
```

## MLflow

MLflow is used to track:

```text
model parameters
model metrics
classification reports
confusion matrices
trained model artifacts
cross-validation results
GridSearchCV results
```

Local MLflow files are ignored by Git:

```text
mlflow.db
mlruns/
mlartifacts/
```

## Conclusion

Random Forest is currently the strongest model in this project, especially for draw prediction.

However, the model is still weak overall. GridSearchCV tuning only produced marginal gains, and several attempted feature/model experiments did not improve the results enough to keep.

The main limitation is likely the small dataset and limited available pre-match information.

The next meaningful improvement would probably come from:

```text
more seasons of data
better pre-match features
more reliable team-strength signals
```

This project should not present the current model as a strong final predictor. It is better described as a complete, honest ML workflow with clear evaluation and experiment tracking.
