
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

OUTPUT_PATH = OUTPUT_DIR / "complaint_text_dataset.csv"


def main():

    print("Preparing complaint text classification dataset...")

    dataframe = pd.read_csv(INPUT_PATH)

    required_columns = [
        "request_id",
        "title",
        "description",
        "category_name",
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

    # Select required columns
    dataframe = dataframe[required_columns].copy()

    # Remove records without text or target category
    dataframe = dataframe.dropna(
        subset=["title", "description", "category_name"]
    )

    # Convert text columns to strings
    dataframe["title"] = dataframe["title"].astype(str).str.strip()
    dataframe["description"] = (
        dataframe["description"].astype(str).str.strip()
    )

    dataframe["category_name"] = (
        dataframe["category_name"].astype(str).str.strip()
    )

    # Remove empty text records
    dataframe = dataframe[
        (dataframe["title"] != "")
        & (dataframe["description"] != "")
        & (dataframe["category_name"] != "")
    ]

    # Remove duplicate complaint IDs
    dataframe = dataframe.drop_duplicates(
        subset=["request_id"]
    )

    dataframe.to_csv(OUTPUT_PATH, index=False)

    print("\nDataset prepared successfully.")
    print("Shape:", dataframe.shape)

    print("\nComplaint category distribution:")
    print(dataframe["category_name"].value_counts())

    print("\nMissing values:")
    print(dataframe.isnull().sum())

    print("\nSaved dataset:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
