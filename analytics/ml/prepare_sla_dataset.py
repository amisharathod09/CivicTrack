from pathlib import Path
import pandas as pd

from analytics.db_connection import engine


PROJECT_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = (
    PROJECT_DIR
    / "analytics"
    / "outputs"
    / "ml"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


QUERY = """
SELECT
    sr.request_id,
    sr.title,
    sr.description,
    c.category_name,
    d.department_name,
    sr.priority,
    l.area,
    l.city,
    l.state,
    DAYOFWEEK(sr.created_at) AS submission_day,
    HOUR(sr.created_at) AS submission_hour,
    CASE
        WHEN sr.resolved_at > sr.sla_due_at THEN 1
        ELSE 0
    END AS sla_breached

FROM service_requests sr

JOIN categories c
    ON sr.category_id = c.category_id

JOIN departments d
    ON c.department_id = d.department_id

JOIN locations l
    ON sr.location_id = l.location_id

WHERE
    sr.sla_due_at IS NOT NULL
    AND sr.resolved_at IS NOT NULL

ORDER BY sr.request_id;
"""


def prepare_sla_dataset():

    print("\nPreparing CivicTrack SLA dataset...\n")

    with engine.connect() as connection:
        dataframe = pd.read_sql(
            QUERY,
            connection
        )

    if dataframe.empty:
        raise ValueError(
            "No completed complaints with SLA deadlines found."
        )

    # Check target values
    if dataframe["sla_breached"].isnull().any():
        raise ValueError("SLA target contains missing values.")

    dataframe["sla_breached"] = (
        dataframe["sla_breached"].astype(int)
    )

    # Save dataset
    output_path = (
        OUTPUT_DIR / "sla_prediction_dataset.csv"
    )

    dataframe.to_csv(
        output_path,
        index=False
    )

    print("SLA dataset prepared successfully!")

    print("\nDataset shape:")
    print(dataframe.shape)

    print("\nSLA outcome distribution:")
    print(
        dataframe["sla_breached"].value_counts()
        .sort_index()
        .rename({
            0: "Within SLA",
            1: "Breached SLA"
        })
    )

    print("\nSaved to:")
    print(output_path)


if __name__ == "__main__":
    prepare_sla_dataset()