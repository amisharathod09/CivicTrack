
from pathlib import Path

import pandas as pd


# Project directories
PROJECT_DIR = Path(__file__).resolve().parents[2]

RAW_DIR = (
    PROJECT_DIR / "analytics" / "outputs" / "etl" / "raw"
)

PROCESSED_DIR = (
    PROJECT_DIR / "analytics" / "outputs" / "etl" / "processed"
)

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


VALID_PRIORITIES = ["Low", "Medium", "High", "Critical"]

VALID_STATUSES = [
    "Submitted", "Assigned", "In Progress",
    "Resolved", "Closed", "Cancelled"
]

quality_report = []


def record_quality(dataset, check, result, details=""):
    quality_report.append({
        "dataset": dataset,
        "check": check,
        "result": result,
        "details": details
    })


def load_raw_dataset(name):

    file_path = RAW_DIR / f"{name}.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Missing raw dataset: {file_path}")

    df = pd.read_csv(file_path)

    original_rows = len(df)
    duplicate_count = int(df.duplicated().sum())

    df = df.drop_duplicates().copy()

    record_quality(
        name,
        "Duplicate rows",
        "PASS" if duplicate_count == 0 else "REMOVED",
        f"{duplicate_count} duplicate rows removed"
    )

    print(f"\nProcessing {name}: {len(df)} rows")

    return df


def parse_dates(df, columns, dataset):

    for column in columns:

        parsed = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        invalid = int(
            (df[column].notna() & parsed.isna()).sum()
        )

        if invalid:
            raise ValueError(
                f"{dataset}: Invalid dates in {column}"
            )

        df[column] = parsed

        record_quality(
            dataset,
            f"{column} validation",
            "PASS",
            f"{int(parsed.isna().sum())} missing values preserved"
        )


def save_dataset(df, name):

    output_file = PROCESSED_DIR / f"cleaned_{name}.csv"

    df.to_csv(output_file, index=False)

    print(f"Saved: {output_file.name}")


def transform_complaints():

    name = "complaints"
    df = load_raw_dataset(name)

    text_columns = [
        "title", "description", "priority", "status",
        "category_name", "department_name",
        "area", "city", "state"
    ]

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()

    parse_dates(
        df,
        ["created_at", "resolved_at"],
        name
    )

    if df["request_id"].isna().any() or df["request_id"].duplicated().any():
        raise ValueError("Complaint IDs must be unique and present.")

    if df[["title", "created_at", "priority", "status"]].isna().any().any():
        raise ValueError("Required complaint values are missing.")

    if not df["priority"].isin(VALID_PRIORITIES).all():
        raise ValueError("Invalid complaint priority found.")

    if not df["status"].isin(VALID_STATUSES).all():
        raise ValueError("Invalid complaint status found.")

    if (df["resolved_at"] < df["created_at"]).any():
        raise ValueError("Resolution date precedes creation date.")

    completed = df["status"].isin(["Resolved", "Closed"])

    if df.loc[completed, "resolved_at"].isna().any():
        raise ValueError("Completed complaints need resolution dates.")

    if df.loc[~completed, "resolved_at"].notna().any():
        raise ValueError("Non-completed complaint has a resolution date.")

    record_quality(name, "Complaint validation", "PASS",
                   "IDs, priorities, statuses and dates are valid")

    save_dataset(df, name)

    return df


def transform_resolution_metrics():

    name = "resolution_metrics"
    df = load_raw_dataset(name)

    parse_dates(df, ["created_at", "resolved_at"], name)

    df["resolution_hours"] = pd.to_numeric(
        df["resolution_hours"],
        errors="raise"
    )

    if df["request_id"].isna().any() or df["request_id"].duplicated().any():
        raise ValueError("Resolution request IDs must be unique.")

    if df["resolution_hours"].isna().any() or (df["resolution_hours"] < 0).any():
        raise ValueError("Invalid resolution hours found.")

    if not df["status"].isin(["Resolved", "Closed"]).all():
        raise ValueError("Non-completed complaint in resolution metrics.")

    q1 = df["resolution_hours"].quantile(0.25)
    q3 = df["resolution_hours"].quantile(0.75)
    iqr = q3 - q1
    upper_limit = q3 + (1.5 * iqr)

    df["resolution_time_outlier"] = (
        df["resolution_hours"] > upper_limit
    )

    outlier_count = int(df["resolution_time_outlier"].sum())

    record_quality(
        name,
        "Resolution time outliers",
        "FLAGGED",
        f"{outlier_count} flagged; none removed. Upper limit: {upper_limit:.2f} hours"
    )

    save_dataset(df, name)

    return df


def transform_department_summary():

    name = "department_summary"
    df = load_raw_dataset(name)

    numeric_columns = [
        "total_complaints", "submitted_complaints",
        "assigned_complaints", "in_progress_complaints",
        "resolved_complaints", "closed_complaints",
        "cancelled_complaints"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="raise")

    if df[numeric_columns].isna().any().any():
        raise ValueError("Missing department counts.")

    if (df[numeric_columns] < 0).any().any():
        raise ValueError("Negative department counts.")

    status_total = df[
        [
            "submitted_complaints", "assigned_complaints",
            "in_progress_complaints", "resolved_complaints",
            "closed_complaints", "cancelled_complaints"
        ]
    ].sum(axis=1)

    if not status_total.eq(df["total_complaints"]).all():
        raise ValueError("Department counts do not match totals.")

    record_quality(name, "Department counts", "PASS", "Counts are consistent")

    save_dataset(df, name)

    return df


def transform_monthly_trends():

    name = "monthly_trends"
    df = load_raw_dataset(name)

    df["complaint_year"] = pd.to_numeric(
        df["complaint_year"], errors="raise"
    )

    df["complaint_month"] = pd.to_numeric(
        df["complaint_month"], errors="raise"
    )

    df["total_complaints"] = pd.to_numeric(
        df["total_complaints"], errors="raise"
    )

    if df["complaint_period"].isna().any():
        raise ValueError("Missing monthly periods.")

    if df["complaint_period"].duplicated().any():
        raise ValueError("Duplicate monthly periods.")

    if not df["complaint_month"].between(1, 12).all():
        raise ValueError("Invalid month numbers.")

    if df["total_complaints"].isna().any() or (df["total_complaints"] < 0).any():
        raise ValueError("Invalid monthly complaint counts.")

    df["complaint_year"] = df["complaint_year"].astype(int)
    df["complaint_month"] = df["complaint_month"].astype(int)

    record_quality(name, "Monthly trends", "PASS", "Monthly data validated")

    save_dataset(df, name)

    return df


def transform_staff_workload():

    name = "staff_workload"
    df = load_raw_dataset(name)

    df["current_assigned_complaints"] = pd.to_numeric(
        df["current_assigned_complaints"],
        errors="raise"
    )

    if df["staff_id"].isna().any() or df["staff_id"].duplicated().any():
        raise ValueError("Staff IDs must be unique and present.")

    if df["current_assigned_complaints"].isna().any():
        raise ValueError("Missing staff assignment counts.")

    if (df["current_assigned_complaints"] < 0).any():
        raise ValueError("Negative staff assignment counts.")

    record_quality(name, "Staff workload", "PASS", "Assignment counts validated")

    save_dataset(df, name)

    return df


def transform_feedback_ratings():

    name = "feedback_ratings"
    df = load_raw_dataset(name)

    parse_dates(df, ["created_at"], name)

    if df["feedback_id"].isna().any() or df["feedback_id"].duplicated().any():
        raise ValueError("Feedback IDs must be unique and present.")

    if df["request_id"].isna().any() or df["rating"].isna().any():
        raise ValueError("Missing feedback request ID or rating.")

    df["rating"] = pd.to_numeric(df["rating"], errors="raise")

    if not df["rating"].between(1, 5).all():
        raise ValueError("Feedback ratings must be between 1 and 5.")

    if not (df["rating"] % 1 == 0).all():
        raise ValueError("Feedback ratings must be whole numbers.")

    df["rating"] = df["rating"].astype(int)

    record_quality(name, "Feedback ratings", "PASS", "Ratings are valid")

    save_dataset(df, name)

    return df


def transform_status_history(valid_request_ids):

    name = "status_history"
    df = load_raw_dataset(name)

    parse_dates(df, ["changed_at"], name)

    if df["history_id"].isna().any() or df["history_id"].duplicated().any():
        raise ValueError("History IDs must be unique and present.")

    if df["request_id"].isna().any():
        raise ValueError("Missing history request IDs.")

    if not df["request_id"].isin(valid_request_ids).all():
        raise ValueError("History contains unknown complaint IDs.")

    if df["new_status"].isna().any():
        raise ValueError("Missing new status values.")

    if not df["new_status"].isin(VALID_STATUSES).all():
        raise ValueError("Invalid new status values.")

    if not df["old_status"].dropna().isin(VALID_STATUSES).all():
        raise ValueError("Invalid old status values.")

    initial_records = df["old_status"].isna()

    if not (df.loc[initial_records, "new_status"] == "Submitted").all():
        raise ValueError("Invalid initial submission history.")

    record_quality(
        name,
        "History validation",
        "PASS",
        f"{int(initial_records.sum())} initial submissions preserved"
    )

    save_dataset(df, name)

    return df


def transform_datasets():

    global quality_report

    quality_report = []

    print("\nStarting CivicTrack ETL transformation...\n")

    complaints = transform_complaints()
    resolution = transform_resolution_metrics()
    department = transform_department_summary()
    monthly = transform_monthly_trends()
    staff = transform_staff_workload()
    feedback = transform_feedback_ratings()
    history = transform_status_history(set(complaints["request_id"]))

    if int(department["total_complaints"].sum()) != len(complaints):
        raise ValueError("Department total does not match complaints.")

    if int(monthly["total_complaints"].sum()) != len(complaints):
        raise ValueError("Monthly total does not match complaints.")

    if not feedback["request_id"].isin(complaints["request_id"]).all():
        raise ValueError("Feedback contains unknown complaint IDs.")

    record_quality(
        "cross_dataset",
        "Complaint totals and references",
        "PASS",
        "Department, monthly and feedback references validated"
    )

    report = pd.DataFrame(quality_report)

    report.to_csv(
        PROCESSED_DIR / "data_quality_report.csv",
        index=False
    )

    print("\nETL transformation completed successfully!")
    print("Complaints:", len(complaints))
    print("Resolution metrics:", len(resolution))
    print("Departments:", len(department))
    print("Monthly periods:", len(monthly))
    print("Staff:", len(staff))
    print("Feedback:", len(feedback))
    print("Status history:", len(history))
    print("\nData quality report saved.")


if __name__ == "__main__":
    transform_datasets()
