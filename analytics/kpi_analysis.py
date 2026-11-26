
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "analytics" / "outputs"

print("\n======================================")
print("CIVICTRACK BUSINESS KPI ANALYSIS")
print("======================================")

# Load cleaned datasets
complaints = pd.read_csv(
    OUTPUT_DIR / "cleaned_complaints.csv",
    parse_dates=["created_at", "resolved_at"]
)

resolution = pd.read_csv(
    OUTPUT_DIR / "cleaned_resolution_metrics.csv"
)

departments = pd.read_csv(
    OUTPUT_DIR / "cleaned_department_summary.csv"
)

monthly = pd.read_csv(
    OUTPUT_DIR / "cleaned_monthly_trends.csv"
)

staff = pd.read_csv(
    OUTPUT_DIR / "cleaned_staff_workload.csv"
)

feedback = pd.read_csv(
    OUTPUT_DIR / "cleaned_feedback_ratings.csv"
)

# --------------------------------------------------
# 1. OVERALL COMPLAINT KPIs
# --------------------------------------------------

total_complaints = len(complaints)

resolved_count = complaints["status"].isin(
    ["Resolved", "Closed"]
).sum()

active_count = complaints["status"].isin(
    ["Submitted", "Assigned", "In Progress"]
).sum()

cancelled_count = complaints["status"].eq("Cancelled").sum()

resolution_rate = (
    resolved_count / total_complaints * 100
    if total_complaints else 0
)

cancellation_rate = (
    cancelled_count / total_complaints * 100
    if total_complaints else 0
)

print("\n1. OVERALL COMPLAINT KPIs")
print("-" * 45)
print("Total complaints:", total_complaints)
print("Resolved/Closed:", resolved_count)
print("Active complaints:", active_count)
print("Cancelled complaints:", cancelled_count)
print(f"Resolution rate: {resolution_rate:.2f}%")
print(f"Cancellation rate: {cancellation_rate:.2f}%")


# --------------------------------------------------
# 2. AVERAGE RESOLUTION TIME
# --------------------------------------------------

average_resolution_hours = resolution["resolution_hours"].mean()
median_resolution_hours = resolution["resolution_hours"].median()

average_resolution_days = average_resolution_hours / 24

print("\n2. RESOLUTION TIME")
print("-" * 45)
print(f"Average resolution time: {average_resolution_hours:.2f} hours")
print(f"Average resolution time: {average_resolution_days:.2f} days")
print(f"Median resolution time: {median_resolution_hours:.2f} hours")

# Compare average with outliers excluded for diagnostic purposes.
# This is not the official KPI; all records remain in the dataset.
normal_resolution = resolution.loc[
    ~resolution["resolution_time_outlier"],
    "resolution_hours"
]

if not normal_resolution.empty:
    print(
        "Average excluding flagged outliers:",
        f"{normal_resolution.mean():.2f} hours"
    )


# --------------------------------------------------
# 3. PRIORITY-WISE COMPLAINT DISTRIBUTION
# --------------------------------------------------

priority_summary = (
    complaints.groupby("priority")
    .size()
    .reset_index(name="total_complaints")
)

priority_summary["percentage"] = (
    priority_summary["total_complaints"] / total_complaints * 100
).round(2)

priority_summary = priority_summary.sort_values(
    "total_complaints", ascending=False
)

print("\n3. PRIORITY-WISE DISTRIBUTION")
print("-" * 45)
print(priority_summary.to_string(index=False))


# --------------------------------------------------
# 4. STATUS-WISE COMPLAINT DISTRIBUTION
# --------------------------------------------------

status_summary = (
    complaints.groupby("status")
    .size()
    .reset_index(name="total_complaints")
)

status_summary["percentage"] = (
    status_summary["total_complaints"] / total_complaints * 100
).round(2)

print("\n4. STATUS-WISE DISTRIBUTION")
print("-" * 45)
print(status_summary.to_string(index=False))


# --------------------------------------------------
# 5. DEPARTMENT PERFORMANCE
# --------------------------------------------------

departments["completed_complaints"] = (
    departments["resolved_complaints"]
    + departments["closed_complaints"]
)

departments["active_complaints"] = (
    departments["submitted_complaints"]
    + departments["assigned_complaints"]
    + departments["in_progress_complaints"]
)

departments["resolution_rate"] = (
    departments["completed_complaints"]
    / departments["total_complaints"].replace(0, pd.NA)
    * 100
).fillna(0).round(2)

department_performance = departments[
    [
        "department_name",
        "total_complaints",
        "active_complaints",
        "completed_complaints",
        "cancelled_complaints",
        "resolution_rate"
    ]
].sort_values("resolution_rate", ascending=False)

print("\n5. DEPARTMENT PERFORMANCE")
print("-" * 45)
print(department_performance.to_string(index=False))


# --------------------------------------------------
# 6. AREA-WISE COMPLAINT DISTRIBUTION
# --------------------------------------------------

area_summary = (
    complaints.groupby("area")
    .size()
    .reset_index(name="total_complaints")
    .sort_values("total_complaints", ascending=False)
)

print("\n6. AREA-WISE COMPLAINT DISTRIBUTION")
print("-" * 45)
print(area_summary.to_string(index=False))


# --------------------------------------------------
# 7. MONTHLY COMPLAINT TREND
# --------------------------------------------------

monthly_summary = monthly[
    ["complaint_period", "total_complaints"]
].sort_values("complaint_period")

print("\n7. MONTHLY COMPLAINT TREND")
print("-" * 45)
print(monthly_summary.to_string(index=False))


# --------------------------------------------------
# 8. CITIZEN FEEDBACK
# --------------------------------------------------

average_rating = feedback["rating"].mean()

rating_distribution = (
    feedback.groupby("rating")
    .size()
    .reset_index(name="feedback_count")
    .sort_values("rating")
)

print("\n8. CITIZEN FEEDBACK")
print("-" * 45)
print("Total feedback records:", len(feedback))
print(f"Average citizen rating: {average_rating:.2f}/5")
print(rating_distribution.to_string(index=False))


# --------------------------------------------------
# 9. CURRENT STAFF WORKLOAD
# --------------------------------------------------

staff_summary = staff[
    [
        "staff_name",
        "department_name",
        "current_assigned_complaints"
    ]
].sort_values(
    "current_assigned_complaints",
    ascending=False
)

print("\n9. CURRENT STAFF WORKLOAD")
print("-" * 45)
print(staff_summary.to_string(index=False))


# --------------------------------------------------
# 10. SAVE KPI OUTPUTS
# --------------------------------------------------

kpi_summary = pd.DataFrame([
    {"metric": "Total Complaints", "value": total_complaints},
    {"metric": "Resolved and Closed Complaints", "value": resolved_count},
    {"metric": "Active Complaints", "value": active_count},
    {"metric": "Cancelled Complaints", "value": cancelled_count},
    {"metric": "Resolution Rate (%)", "value": round(resolution_rate, 2)},
    {"metric": "Cancellation Rate (%)", "value": round(cancellation_rate, 2)},
    {"metric": "Average Resolution Hours", "value": round(average_resolution_hours, 2)},
    {"metric": "Median Resolution Hours", "value": round(median_resolution_hours, 2)},
    {"metric": "Average Feedback Rating", "value": round(average_rating, 2)}
])

kpi_summary.to_csv(
    OUTPUT_DIR / "kpi_summary.csv",
    index=False
)

priority_summary.to_csv(
    OUTPUT_DIR / "priority_analysis.csv",
    index=False
)

status_summary.to_csv(
    OUTPUT_DIR / "status_analysis.csv",
    index=False
)

department_performance.to_csv(
    OUTPUT_DIR / "department_performance.csv",
    index=False
)

area_summary.to_csv(
    OUTPUT_DIR / "area_analysis.csv",
    index=False
)

monthly_summary.to_csv(
    OUTPUT_DIR / "monthly_analysis.csv",
    index=False
)

rating_distribution.to_csv(
    OUTPUT_DIR / "feedback_analysis.csv",
    index=False
)

staff_summary.to_csv(
    OUTPUT_DIR / "staff_workload_analysis.csv",
    index=False
)

print("\n======================================")
print("KPI ANALYSIS COMPLETED SUCCESSFULLY")
print("======================================")
print("\nEight KPI analysis files saved in analytics/outputs/")
