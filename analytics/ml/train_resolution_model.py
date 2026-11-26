
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# Project paths
PROJECT_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_DIR
    / "analytics"
    / "outputs"
    / "etl"
    / "processed"
    / "cleaned_resolution_metrics.csv"
)

MODEL_DIR = PROJECT_DIR / "analytics" / "outputs" / "ml" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "resolution_time_model.joblib"


def main():

    print("Starting experimental resolution-time model training...")

    # Load dataset
    dataframe = pd.read_csv(DATA_PATH)

    # Convert submission timestamp
    dataframe["created_at"] = pd.to_datetime(dataframe["created_at"])

    dataframe["submission_day"] = dataframe["created_at"].dt.dayofweek
    dataframe["submission_hour"] = dataframe["created_at"].dt.hour

    # Input features
    features = [
        "title",
        "priority",
        "category_name",
        "department_name",
        "submission_day",
        "submission_hour",
    ]

    X = dataframe[features]
    y = dataframe["resolution_hours"]

    print("\nDataset shape:", dataframe.shape)
    print("Total records:", len(dataframe))
    print("\nResolution time statistics:")
    print(y.describe())

    # Text and categorical preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "title",
                TfidfVectorizer(max_features=100),
                "title",
            ),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                [
                    "priority",
                    "category_name",
                    "department_name",
                ],
            ),
            (
                "numerical",
                SimpleImputer(strategy="median"),
                [
                    "submission_day",
                    "submission_hour",
                ],
            ),
        ]
    )

    # Regression pipeline
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=100,
                    max_depth=4,
                    min_samples_leaf=2,
                    random_state=42,
                ),
            ),
        ]
    )

    # Cross-validation
    cross_validation = KFold(
        n_splits=5,
        shuffle=True,
        random_state=42,
    )

    predictions = cross_val_predict(
        model,
        X,
        y,
        cv=cross_validation,
    )

    # Evaluation
    mae = mean_absolute_error(y, predictions)
    rmse = np.sqrt(mean_squared_error(y, predictions))
    r2 = r2_score(y, predictions)

    print("\nExperimental Cross-Validation Results")
    print("-------------------------------------")
    print(f"MAE: {mae:.2f} hours")
    print(f"RMSE: {rmse:.2f} hours")
    print(f"R2 Score: {r2:.4f}")

    # Train final model on all available records
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)

    print("\nModel saved successfully:")
    print(MODEL_PATH)

    print(
        "\nWARNING: This model is experimental. "
        "Only 19 historical records are available. "
        "Do not use predictions for real operational decisions."
    )


if __name__ == "__main__":
    main()

