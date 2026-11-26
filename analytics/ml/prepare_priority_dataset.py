
from pathlib import Path

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[2]

INPUT_PATH = (
    PROJECT_DIR
    / "analytics"
    / "outputs"
    / "etl"
    / "processed"
    / "cleaned_complaints.csv"
)

OUTPUT_DIR = PROJECT_DIR / "analytics" / "outputs" / "ml"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "priority_classification_dataset.csv"


def main():

    print("Preparing priority classification dataset...")

    dataframe = pd.read_csv(INPUT_PATH)

    required_columns = [
        "request_id",
        "title",
        "description",
        "priority",
        "category_name",
        "department_name",
        "area",
        "created_at",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Keep only required fields
    dataframe = dataframe[required_columns].copy()

    # Remove records with missing target or essential text
    dataframe = dataframe.dropna(
        subset=["priority", "title", "description"]
    )

    # Convert submission timestamp
    dataframe["created_at"] = pd.to_datetime(
        dataframe["created_at"],
        errors="coerce"
    )

    dataframe = dataframe.dropna(subset=["created_at"])

    dataframe["submission_day"] = (
        dataframe["created_at"].dt.day_of_week
    )

    dataframe["submission_hour"] = (
        dataframe["created_at"].dt.hour
    )

    # Remove timestamp after extracting features
    dataframe = dataframe.drop(columns=["created_at"])

    # Remove duplicate complaint IDs
    dataframe = dataframe.drop_duplicates(
        subset=["request_id"]
    )

    dataframe.to_csv(OUTPUT_PATH, index=False)

    print("\nDataset prepared successfully.")
    print("Shape:", dataframe.shape)

    print("\nPriority distribution:")
    print(dataframe["priority"].value_counts())

    print("\nMissing values:")
    print(dataframe.isnull().sum())

    print("\nSaved dataset:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
