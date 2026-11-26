
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_predict,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


PROJECT_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_DIR
    / "analytics"
    / "outputs"
    / "ml"
    / "priority_classification_dataset.csv"
)

MODEL_DIR = PROJECT_DIR / "analytics" / "outputs" / "ml" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "priority_classification_model.joblib"


def main():

    print("Starting experimental priority classification...")

    dataframe = pd.read_csv(DATA_PATH)

    # Remove identifier from model inputs
    features = [
        "title",
        "description",
        "category_name",
        "department_name",
        "area",
        "submission_day",
        "submission_hour",
    ]

    X = dataframe[features]
    y = dataframe["priority"]

    print("\nDataset shape:", dataframe.shape)

    print("\nPriority distribution:")
    print(y.value_counts())

    # Preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "title",
                TfidfVectorizer(max_features=100),
                "title",
            ),
            (
                "description",
                TfidfVectorizer(max_features=200),
                "description",
            ),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                [
                    "category_name",
                    "department_name",
                    "area",
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

    # Classification pipeline
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=42,
                ),
            ),
        ]
    )

    # Stratified cross-validation
    cross_validation = StratifiedKFold(
        n_splits=3,
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
    print("\nExperimental Cross-Validation Results")
    print("-------------------------------------")

    print(
        "Accuracy:",
        round(accuracy_score(y, predictions), 4),
    )

    print(
        "Balanced Accuracy:",
        round(balanced_accuracy_score(y, predictions), 4),
    )

    print(
        "Macro F1 Score:",
        round(f1_score(y, predictions, average="macro"), 4),
    )

    print("\nConfusion Matrix:")
    print(confusion_matrix(y, predictions, labels=[
        "Critical", "High", "Low", "Medium"
    ]))

    print("\nClassification Report:")
    print(
        classification_report(
            y,
            predictions,
            labels=["Critical", "High", "Low", "Medium"],
            zero_division=0,
        )
    )

    # Train final model on all available records
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)

    print("\nModel saved successfully:")
    print(MODEL_PATH)

    print(
        "\nWARNING: Experimental model only. "
        "Only 37 historical complaints are available. "
        "Do not use predictions for real operational decisions."
    )


if __name__ == "__main__":
    main()
