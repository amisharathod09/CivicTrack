
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "analytics" / "outputs"
POWERBI_DIR = OUTPUT_DIR / "powerbi"

POWERBI_DIR.mkdir(parents=True, exist_ok=True)

print("\n======================================")
print("CIVICTRACK POWER BI DATA EXPORT")
print("======================================")

# --------------------------------------------------
# 1. LOAD CLEANED DATASETS
# --------------------------------------------------

complaints = pd.read_csv(
    OUTPUT_DIR / "cleaned_complaints.csv",
    parse_dates=["created_at", "resolved_at"]
)

resolution = pd.read_csv(
    OUTPUT_DIR / "cleaned_resolution_metrics.csv",
    parse_dates=["created_at", "resolved_at"]
)

departments = pd.read_csv(
    OUTPUT_DIR / "department_performance.csv"
)

monthly = pd.read_csv(
    OUTPUT_DIR / "monthly_analysis.csv"
)

areas = pd.read_csv(
    OUTPUT_DIR / "area_analysis.csv"
)

feedback = pd.read_csv(
    OUTPUT_DIR / "cleaned_feedback_ratings.csv",
    parse_dates=["created_at"]
)

staff = pd.read_csv(
    OUTPUT_DIR / "staff_workload_analysis.csv"
)

quality = pd.read_csv(
    OUTPUT_DIR / "data_quality_report.csv"
)


# --------------------------------------------------
# 2. PREPARE COMPLAINT FACT DATASET
# --------------------------------------------------

complaints["created_date"] = complaints["created_at"].dt.date
complaints["created_year"] = complaints["created_at"].dt.year
complaints["created_month"] = complaints["created_at"].dt.month
complaints["created_month_name"] = complaints["created_at"].dt.strftime("%B")
complaints["created_period"] = complaints["created_at"].dt.strftime("%Y-%m")

complaints["is_completed"] = complaints["status"].isin(
    ["Resolved", "Closed"]
).astype(int)

complaints["is_active"] = complaints["status"].isin(
    ["Submitted", "Assigned", "In Progress"]
).astype(int)

complaints["is_cancelled"] = (
    complaints["status"] == "Cancelled"
).astype(int)

complaints["is_high_priority"] = complaints["priority"].isin(
    ["High", "Critical"]
).astype(int)

complaints["resolution_hours"] = (
    complaints["resolved_at"] - complaints["created_at"]
).dt.total_seconds() / 3600

# Exclude personal citizen information.
complaint_columns = [
    "request_id",
    "title",
    "description",
    "priority",
    "status",
    "created_at",
    "created_date",
    "created_year",
    "created_month",
    "created_month_name",
    "created_period",
    "resolved_at",
    "resolution_hours",
    "is_completed",
    "is_active",
    "is_cancelled",
    "is_high_priority",
    "category_name",
    "department_name",
    "area",
    "city",
    "state"
]

complaint_export = complaints[complaint_columns].copy()


# --------------------------------------------------
# 3. PREPARE RESOLUTION ANALYSIS
# --------------------------------------------------

resolution_export = resolution.copy()

resolution_export["resolution_days"] = (
    resolution_export["resolution_hours"] / 24
).round(2)


# --------------------------------------------------
# 4. PREPARE DEPARTMENT PERFORMANCE
# --------------------------------------------------

department_export = departments.copy()

department_export["resolution_rate"] = (
    department_export["resolution_rate"].round(2)
)


# --------------------------------------------------
# 5. PREPARE MONTHLY TREND
# --------------------------------------------------

monthly_export = monthly.copy()

monthly_export["complaint_year"] = (
    monthly_export["complaint_period"].str[:4].astype(int)
)

monthly_export["complaint_month"] = (
    monthly_export["complaint_period"].str[5:7].astype(int)
)


# --------------------------------------------------
# 6. PREPARE AREA ANALYSIS
# --------------------------------------------------

area_export = areas.copy()


# --------------------------------------------------
# 7. PREPARE FEEDBACK ANALYSIS
# --------------------------------------------------

feedback_export = feedback.copy()

feedback_export["feedback_date"] = (
    feedback_export["created_at"].dt.date
)


# --------------------------------------------------
# 8. PREPARE STAFF WORKLOAD
# --------------------------------------------------

staff_export = staff.copy()


# --------------------------------------------------
# 9. PREPARE SLA PERFORMANCE DATA
# --------------------------------------------------
# This is the existing operational SQL result.
# Do not recalculate SLA compliance from resolution time.

sla_summary = pd.DataFrame([{
    "total_eligible_complaints": 29,
    "completed_complaints": 18,
    "resolved_within_sla": 15,
    "resolved_after_sla": 3,
    "active_overdue_complaints": 11,
    "sla_compliance_rate": 83.33
}])


# --------------------------------------------------
# 10. EXPORT DATASETS
# --------------------------------------------------

datasets = {
    "fact_complaints.csv": complaint_export,
    "resolution_analysis.csv": resolution_export,
    "department_performance.csv": department_export,
    "monthly_trends.csv": monthly_export,
    "area_analysis.csv": area_export,
    "feedback_analysis.csv": feedback_export,
    "staff_workload.csv": staff_export,
    "sla_summary.csv": sla_summary,
    "data_quality_report.csv": quality
}

print("\nExporting Power BI datasets...\n")

for filename, dataframe in datasets.items():

    file_path = POWERBI_DIR / filename

    dataframe.to_csv(
        file_path,
        index=False,
        date_format="%Y-%m-%d %H:%M:%S"
    )

    print(
        f"{filename:<35} "
        f"Rows: {len(dataframe):<5} "
        f"Columns: {len(dataframe.columns)}"
    )

print("\n======================================")
print("POWER BI EXPORT COMPLETED")
print("======================================")
print("Total datasets:", len(datasets))
print("Export folder:", POWERBI_DIR)
