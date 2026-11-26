from pathlib import Path
import pandas as pd

from sqlalchemy import create_engine, URL
from dotenv import load_dotenv
import os

# Project paths
PROJECT_DIR = Path(__file__).resolve().parents[2]

PROCESSED_DIR = (
    PROJECT_DIR
    / "analytics"
    / "outputs"
    / "etl"
    / "processed"
)

# Load existing backend environment variables
ENV_PATH = PROJECT_DIR / "backend" / ".env"
load_dotenv(ENV_PATH)

# Database configuration
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")

DB_NAME = "civictrack_analytics"

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME
)

engine = create_engine(DATABASE_URL)
# Source CSV files and destination table names
DATASETS = {
    "complaints": "etl_complaints",
    "resolution_metrics": "etl_resolution_metrics",
    "department_summary": "etl_department_summary",
    "monthly_trends": "etl_monthly_trends",
    "staff_workload": "etl_staff_workload",
    "feedback_ratings": "etl_feedback_ratings",
    "status_history": "etl_status_history"
}

def load_datasets():
    """
    Load transformed CSV datasets into MySQL analytics tables.
    """

    print("\nStarting CivicTrack ETL loading...\n")

    if not PROCESSED_DIR.exists():
        raise FileNotFoundError(
            f"Processed directory not found: {PROCESSED_DIR}"
        )

    # Verify database connection
    with engine.connect() as connection:
        print("Connected to civictrack_analytics successfully!")

    for dataset_name, table_name in DATASETS.items():

        file_path = PROCESSED_DIR / f"cleaned_{dataset_name}.csv"

        if not file_path.exists():
            raise FileNotFoundError(
                f"Processed dataset not found: {file_path}"
            )

        dataframe = pd.read_csv(file_path)

        if dataframe.empty:
            print(f"Skipped {dataset_name}: dataset is empty.")
            continue

        dataframe.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=1000
        )

        print(
            f"Loaded {dataset_name}: "
            f"{len(dataframe)} rows -> {table_name}"
        )

    print("\nETL loading completed successfully!")


if __name__ == "__main__":
    load_datasets()