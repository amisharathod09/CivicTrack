
from pathlib import Path

import pandas as pd

from ..db_connection import engine


# Project and output directories
PROJECT_DIR = Path(__file__).resolve().parents[2]

RAW_OUTPUT_DIR = (
    PROJECT_DIR
    / "analytics"
    / "outputs"
    / "etl"
    / "raw"
)

RAW_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# SQL queries for CivicTrack datasets
QUERIES = {
    "complaints": """
        SELECT
            request_id,
            title,
            description,
            priority,
            status,
            created_at,
            resolved_at,
            category_name,
            department_name,
            area,
            city,
            state
        FROM vw_complaint_details
    """,

    "resolution_metrics": """
        SELECT *
        FROM vw_complaint_resolution_metrics
    """,

    "department_summary": """
        SELECT *
        FROM vw_department_complaint_summary
    """,

    "monthly_trends": """
        SELECT *
        FROM vw_monthly_complaint_trends
    """,

    "staff_workload": """
        SELECT *
        FROM vw_staff_workload
    """,

    "feedback_ratings": """
        SELECT
            feedback_id,
            request_id,
            rating,
            created_at
        FROM feedback
    """,

    "status_history": """
        SELECT
            history_id,
            request_id,
            old_status,
            new_status,
            changed_at
        FROM status_history
    """
}


def extract_datasets():

    print("\nStarting CivicTrack ETL extraction...\n")

    extracted_datasets = {}

    with engine.connect() as connection:

        for dataset_name, query in QUERIES.items():

            dataframe = pd.read_sql_query(
                query,
                connection
            )

            output_file = (
                RAW_OUTPUT_DIR / f"{dataset_name}.csv"
            )

            dataframe.to_csv(
                output_file,
                index=False
            )

            extracted_datasets[dataset_name] = dataframe

            print(f"Dataset: {dataset_name}")
            print(f"Rows: {len(dataframe)}")
            print(f"Columns: {len(dataframe.columns)}")
            print(f"Saved: {output_file}")
            print("-" * 45)

    print("\nAll datasets extracted successfully!")

    return extracted_datasets


if __name__ == "__main__":
    extract_datasets()
