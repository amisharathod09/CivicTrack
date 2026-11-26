
from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
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


PROJECT_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_DIR
    / "analytics"
    / "outputs"
    / "ml"
    / "complaint_text_dataset.csv"
)

MODEL_DIR = PROJECT_DIR / "analytics" / "outputs" / "ml" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "complaint_text_model.joblib"


def main():

    print("Starting experimental complaint text classification...")

    dataframe = pd.read_csv(DATA_PATH)

    # Combine title and description
    dataframe["complaint_text"] = (
        dataframe["title"].fillna("")
        + " "
        + dataframe["description"].fillna("")
    )

    X = dataframe["complaint_text"]
    y = dataframe["category_name"]

    print("\nDataset shape:", dataframe.shape)
    print("Total complaints:", len(dataframe))

    print("\nCategory distribution:")
    print(y.value_counts())

    # Text classification pipeline
    model = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    ngram_range=(1, 2),
                    max_features=500,
                ),
            ),
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

    labels = sorted(y.unique())

    print("\nConfusion Matrix:")
    print(confusion_matrix(y, predictions, labels=labels))

    print("\nClassification Report:")
    print(
        classification_report(
            y,
            predictions,
            labels=labels,
            zero_division=0,
        )
    )

    # Train final model using all available records
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)

    print("\nModel saved successfully:")
    print(MODEL_PATH)

    print(
        "\nWARNING: Experimental model only. "
        "Only 37 historical complaints across 10 categories "
        "are available. Do not use predictions for real "
        "operational decisions."
    )


if __name__ == "__main__":
    main()
