from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    balanced_accuracy_score
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_DIR
    / "analytics"
    / "outputs"
    / "ml"
    / "sla_prediction_dataset.csv"
)

MODEL_DIR = PROJECT_DIR / "analytics" / "outputs" / "ml" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def train_sla_model():

    print("\nStarting experimental SLA model training...\n")

    dataframe = pd.read_csv(DATA_PATH)

    target = "sla_breached"

    # Remove identifiers and constant columns.
    excluded_columns = [
        "request_id",
        "city",
        "state",
        target
    ]

    X = dataframe.drop(columns=excluded_columns)
    y = dataframe[target]

    class_counts = y.value_counts()

    print("Class distribution:")
    print(class_counts)

    if y.nunique() != 2 or class_counts.min() < 2:
        raise ValueError(
            "Insufficient examples in one or more target classes."
        )

    # Text features
    text_features = [
        "title",
        "description"
    ]

    # Categorical features
    categorical_features = [
        "category_name",
        "department_name",
        "priority",
        "area"
    ]

    # Numerical features
    numerical_features = [
        "submission_day",
        "submission_hour"
    ]

    title_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=50,
            ngram_range=(1, 2)
        ))
    ])

    description_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=100,
            ngram_range=(1, 2)
        ))
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    numerical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    preprocessor = ColumnTransformer([
        ("title", title_pipeline, "title"),
        ("description", description_pipeline, "description"),
        ("categorical", categorical_pipeline, categorical_features),
        ("numerical", numerical_pipeline, numerical_features)
    ])

    model_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            random_state=42
        ))
    ])

    # Exploratory stratified cross-validation.
    folds = min(3, int(class_counts.min()))

    cv = StratifiedKFold(
        n_splits=folds,
        shuffle=True,
        random_state=42
    )

    predictions = cross_val_predict(
        model_pipeline,
        X,
        y,
        cv=cv,
        method="predict"
    )

    print("\nExploratory cross-validation results:")
    print(
        "Balanced accuracy:",
        round(balanced_accuracy_score(y, predictions), 4)
    )

    print("\nConfusion matrix:")
    print(confusion_matrix(y, predictions, labels=[0, 1]))

    print("\nClassification report:")
    print(
        classification_report(
            y,
            predictions,
            labels=[0, 1],
            target_names=["Within SLA", "Breached SLA"],
            zero_division=0
        )
    )

    # Fit final pipeline on all available examples.
    # This is for an experimental artifact only.
    model_pipeline.fit(X, y)

    model_path = MODEL_DIR / "sla_breach_model.joblib"

    joblib.dump(model_pipeline, model_path)

    print("\nExperimental model saved:")
    print(model_path)

    print(
        "\nWARNING: This model is experimental. "
        "Only three historical breach examples are available. "
        "Do not use its predictions for real operational decisions."
    )


if __name__ == "__main__":
    train_sla_model()