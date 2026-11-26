
from pathlib import Path

import pandas as pd

from db_connection import engine


# Output directory
PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "analytics" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Datasets to extract
queries = {
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

    print("\nStarting CivicTrack data extraction...\n")

    for dataset_name, query in queries.items():

        df = pd.read_sql_query(query, engine)

        output_file = OUTPUT_DIR / f"{dataset_name}.csv"

        df.to_csv(output_file, index=False)

        print(f"Dataset: {dataset_name}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print(f"Saved: {output_file}")
        print("-" * 45)

    print("\nAll datasets extracted successfully!")


if __name__ == "__main__":
    extract_datasets()
