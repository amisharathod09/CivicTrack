
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "analytics" / "outputs"

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


def load_dataset(name):
    file_path = OUTPUT_DIR / f"{name}.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Missing dataset: {file_path}")

    df = pd.read_csv(file_path)
    print(f"\nProcessing {name}: {len(df)} rows")

    original_rows = len(df)
    duplicate_count = int(df.duplicated().sum())

    df = df.drop_duplicates().copy()

    record_quality(
        name, "Duplicate rows",
        "PASS" if duplicate_count == 0 else "REMOVED",
        f"{duplicate_count} duplicate rows"
    )

    record_quality(
        name, "Row count",
        "PASS",
        f"{original_rows} original, {len(df)} after duplicate removal"
    )

    return df


def parse_dates(df, columns, dataset):
    for column in columns:
        parsed = pd.to_datetime(df[column], errors="coerce")
        invalid = int((df[column].notna() & parsed.isna()).sum())

        if invalid:
            raise ValueError(
                f"{dataset}: {invalid} invalid date values in {column}"
            )

        df[column] = parsed

        record_quality(
            dataset, f"{column} validation", "PASS",
            f"{int(parsed.isna().sum())} missing values preserved"
        )


def save_dataset(df, filename):
    output_file = OUTPUT_DIR / filename
    df.to_csv(output_file, index=False)
    print(f"Saved: {output_file.name}")


def clean_complaints():
    name = "complaints"
    df = load_dataset(name)

    text_columns = [
        "title", "description", "priority", "status",
        "category_name", "department_name", "area", "city", "state"
    ]

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()

    parse_dates(df, ["created_at", "resolved_at"], name)

    if df["request_id"].isna().any() or df["request_id"].duplicated().any():
        raise ValueError("Complaints: request_id must be present and unique.")

    if df[["title", "created_at", "priority", "status"]].isna().any().any():
        raise ValueError("Complaints: required values are missing.")

    if not df["priority"].isin(VALID_PRIORITIES).all():
        raise ValueError("Complaints: invalid priority found.")

    if not df["status"].isin(VALID_STATUSES).all():
        raise ValueError("Complaints: invalid status found.")

    if (df["resolved_at"] < df["created_at"]).any():
        raise ValueError("Complaints: resolution date precedes creation date.")

    completed = df["status"].isin(["Resolved", "Closed"])

    if df.loc[completed, "resolved_at"].isna().any():
        raise ValueError("Completed complaints must have a resolution date.")

    if df.loc[~completed, "resolved_at"].notna().any():
        raise ValueError(
            "A non-completed complaint has a resolution date. Review the records."
        )

    record_quality(name, "Request IDs", "PASS", "Unique and present")
    record_quality(name, "Priority and status", "PASS", "All values are valid")
    record_quality(name, "Resolution dates", "PASS", "Date rules satisfied")

    save_dataset(df, "cleaned_complaints.csv")
    return df


def clean_resolution_metrics():
    name = "resolution_metrics"
    df = load_dataset(name)

    parse_dates(df, ["created_at", "resolved_at"], name)

    if df["request_id"].isna().any() or df["request_id"].duplicated().any():
        raise ValueError("Resolution metrics: request_id must be unique.")

    if df["resolution_hours"].isna().any():
        raise ValueError("Resolution metrics: missing resolution hours.")

    if (df["resolution_hours"] < 0).any():
        raise ValueError("Resolution metrics: negative resolution hours found.")

    if not df["status"].isin(["Resolved", "Closed"]).all():
        raise ValueError("Resolution metrics contains a non-completed status.")

    # Identify outliers using the IQR method. Do not remove them.
    q1 = df["resolution_hours"].quantile(0.25)
    q3 = df["resolution_hours"].quantile(0.75)
    iqr = q3 - q1
    upper_limit = q3 + (1.5 * iqr)

    df["resolution_time_outlier"] = (
        df["resolution_hours"] > upper_limit
    )

    outlier_count = int(df["resolution_time_outlier"].sum())

    record_quality(
        name, "Resolution hours", "PASS",
        "All values are non-negative"
    )

    record_quality(
        name, "Resolution time outliers", "FLAGGED",
        f"{outlier_count} records flagged; none removed. Upper IQR limit: {upper_limit:.2f} hours"
    )

    save_dataset(df, "cleaned_resolution_metrics.csv")
    return df


def clean_department_summary():
    name = "department_summary"
    df = load_dataset(name)

    numeric_columns = [
        "total_complaints", "submitted_complaints",
        "assigned_complaints", "in_progress_complaints",
        "resolved_complaints", "closed_complaints",
        "cancelled_complaints"
    ]

    if df[numeric_columns].isna().any().any():
        raise ValueError("Department summary contains missing counts.")

    if (df[numeric_columns] < 0).any().any():
        raise ValueError("Department summary contains negative counts.")

    status_total = df[
        [
            "submitted_complaints", "assigned_complaints",
            "in_progress_complaints", "resolved_complaints",
            "closed_complaints", "cancelled_complaints"
        ]
    ].sum(axis=1)

    if not status_total.eq(df["total_complaints"]).all():
      raise ValueError("Department status counts do not match department totals.")

    record_quality(name, "Department counts", "PASS", "Counts are valid and consistent")

    save_dataset(df, "cleaned_department_summary.csv")
    return df


def clean_monthly_trends():
    name = "monthly_trends"
    df = load_dataset(name)

    if df["complaint_period"].isna().any():
        raise ValueError("Monthly trends contain missing periods.")

    if df["complaint_period"].duplicated().any():
        raise ValueError("Monthly trends contain duplicate periods.")

    if df["total_complaints"].isna().any() or (df["total_complaints"] < 0).any():
        raise ValueError("Monthly trends contain invalid complaint counts.")

    df["complaint_year"] = df["complaint_year"].astype(int)
    df["complaint_month"] = df["complaint_month"].astype(int)

    if not df["complaint_month"].between(1, 12).all():
        raise ValueError("Monthly trends contain invalid month numbers.")

    record_quality(
        name, "Monthly trends", "PASS",
        "Unique periods and non-negative counts; missing months not filled"
    )

    save_dataset(df, "cleaned_monthly_trends.csv")
    return df


def clean_staff_workload():
    name = "staff_workload"
    df = load_dataset(name)

    if df["staff_id"].isna().any() or df["staff_id"].duplicated().any():
        raise ValueError("Staff workload: staff IDs must be unique and present.")

    if df["current_assigned_complaints"].isna().any():
        raise ValueError("Staff workload contains missing assignment counts.")

    if (df["current_assigned_complaints"] < 0).any():
        raise ValueError("Staff workload contains negative assignment counts.")

    record_quality(
        name, "Current workload", "PASS",
        "Staff IDs are unique and assignment counts are valid"
    )

    save_dataset(df, "cleaned_staff_workload.csv")
    return df


def clean_feedback_ratings():
    name = "feedback_ratings"
    df = load_dataset(name)

    parse_dates(df, ["created_at"], name)

    if df["feedback_id"].isna().any() or df["feedback_id"].duplicated().any():
        raise ValueError("Feedback: feedback IDs must be unique and present.")

    if df["request_id"].isna().any():
        raise ValueError("Feedback: request IDs cannot be missing.")

    if df["rating"].isna().any():
        raise ValueError("Feedback: ratings cannot be missing.")

    if not df["rating"].between(1, 5).all():
        raise ValueError("Feedback: ratings must be between 1 and 5.")

    if not (df["rating"] % 1 == 0).all():
        raise ValueError("Feedback: ratings must be whole numbers.")

    df["rating"] = df["rating"].astype(int)

    record_quality(
        name, "Rating validation", "PASS",
        "All ratings are whole numbers between 1 and 5"
    )

    save_dataset(df, "cleaned_feedback_ratings.csv")
    return df


def clean_status_history(valid_request_ids):
    name = "status_history"
    df = load_dataset(name)

    parse_dates(df, ["changed_at"], name)

    if df["history_id"].isna().any() or df["history_id"].duplicated().any():
        raise ValueError("Status history: history IDs must be unique and present.")

    if df["request_id"].isna().any():
        raise ValueError("Status history contains missing request IDs.")

    if not df["request_id"].isin(valid_request_ids).all():
        raise ValueError("Status history refers to unknown complaint IDs.")

    if df["new_status"].isna().any():
        raise ValueError("Status history contains missing new_status values.")

    if not df["new_status"].isin(VALID_STATUSES).all():
        raise ValueError("Status history contains invalid new_status values.")

    if not df["old_status"].dropna().isin(VALID_STATUSES).all():
        raise ValueError("Status history contains invalid old_status values.")

    initial_records = df["old_status"].isna()

    if not (df.loc[initial_records, "new_status"] == "Submitted").all():
        raise ValueError("Missing old_status is only allowed for initial submissions.")

    record_quality(
        name, "Initial status records", "PASS",
        f"{int(initial_records.sum())} initial submissions preserved"
    )

    record_quality(
        name, "Complaint references", "PASS",
        "All history records refer to existing complaints"
    )

    save_dataset(df, "cleaned_status_history.csv")
    return df


def main():
    print("\n======================================")
    print("CIVICTRACK DATA CLEANING PIPELINE")
    print("======================================")

    complaints = clean_complaints()
    resolution = clean_resolution_metrics()
    department = clean_department_summary()
    monthly = clean_monthly_trends()
    staff = clean_staff_workload()
    feedback = clean_feedback_ratings()
    history = clean_status_history(set(complaints["request_id"]))

    if int(department["total_complaints"].sum()) != len(complaints):
        raise ValueError("Department total does not match complaint count.")

    if int(monthly["total_complaints"].sum()) != len(complaints):
        raise ValueError("Monthly total does not match complaint count.")

    record_quality(
        "cross_dataset", "Complaint totals", "PASS",
        "Department and monthly totals match complaint records"
    )

    report = pd.DataFrame(quality_report)
    report.to_csv(OUTPUT_DIR / "data_quality_report.csv", index=False)

    print("\n======================================")
    print("DATA CLEANING COMPLETED SUCCESSFULLY")
    print("======================================")
    print("Complaints:", len(complaints))
    print("Resolution metrics:", len(resolution))
    print("Departments:", len(department))
    print("Monthly periods:", len(monthly))
    print("Staff:", len(staff))
    print("Feedback records:", len(feedback))
    print("Status history:", len(history))
    print("\nQuality report saved: data_quality_report.csv")


if __name__ == "__main__":
    main()
