
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_DIR / "analytics" / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"

CHART_DIR.mkdir(parents=True, exist_ok=True)

# Consistent chart styling
plt.rcParams.update({
    "figure.figsize": (10, 6),
    "figure.dpi": 120,
    "axes.titlesize": 16,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False
})

BLUE = "#2878B5"
TEAL = "#269C94"
GREEN = "#65A98B"
ORANGE = "#E89B52"
PURPLE = "#8B79B7"
GREY = "#82909C"


def save_chart(filename):
    plt.tight_layout()
    plt.savefig(
        CHART_DIR / filename,
        dpi=300,
        bbox_inches="tight",
        facecolor="white"
    )
    plt.close()
    print("Saved chart:", filename)


print("\n======================================")
print("CIVICTRACK EXPLORATORY DATA ANALYSIS")
print("======================================")

# Load cleaned datasets
complaints = pd.read_csv(OUTPUT_DIR / "cleaned_complaints.csv")
resolution = pd.read_csv(OUTPUT_DIR / "cleaned_resolution_metrics.csv")
departments = pd.read_csv(OUTPUT_DIR / "department_performance.csv")
monthly = pd.read_csv(OUTPUT_DIR / "monthly_analysis.csv")
areas = pd.read_csv(OUTPUT_DIR / "area_analysis.csv")
feedback = pd.read_csv(OUTPUT_DIR / "cleaned_feedback_ratings.csv")
staff = pd.read_csv(OUTPUT_DIR / "staff_workload_analysis.csv")


# --------------------------------------------------
# 1. COMPLAINT DISTRIBUTION BY STATUS
# --------------------------------------------------

status_counts = complaints["status"].value_counts()

plt.figure()
bars = plt.bar(
    status_counts.index,
    status_counts.values,
    color=BLUE
)

plt.title("CivicTrack - Complaint Status Distribution")
plt.xlabel("Complaint Status")
plt.ylabel("Number of Complaints")
plt.xticks(rotation=20, ha="right")

for bar in bars:
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        int(bar.get_height()),
        ha="center",
        va="bottom"
    )

save_chart("01_complaint_status.png")


# --------------------------------------------------
# 2. PRIORITY DISTRIBUTION
# --------------------------------------------------

priority_counts = complaints["priority"].value_counts()

priority_order = ["Critical", "High", "Medium", "Low"]
priority_counts = priority_counts.reindex(
    priority_order
).dropna()

plt.figure(figsize=(8, 6))

plt.pie(
    priority_counts.values,
    labels=priority_counts.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=[ORANGE, BLUE, TEAL, GREEN],
    wedgeprops={"width": 0.42, "edgecolor": "white"},
    pctdistance=0.78
)

plt.title("CivicTrack - Complaint Priority Distribution")

save_chart("02_priority_distribution.png")


# --------------------------------------------------
# 3. MONTHLY COMPLAINT TREND
# --------------------------------------------------

monthly = monthly.sort_values("complaint_period")

plt.figure()

plt.plot(
    monthly["complaint_period"],
    monthly["total_complaints"],
    marker="o",
    linewidth=2.5,
    markersize=7,
    color=TEAL
)

plt.title("CivicTrack - Monthly Complaint Trend")
plt.xlabel("Month")
plt.ylabel("Number of Complaints")
plt.xticks(rotation=30, ha="right")
plt.grid(axis="y", alpha=0.25)

for x, y in zip(
    monthly["complaint_period"],
    monthly["total_complaints"]
):
    plt.annotate(
        str(y),
        (x, y),
        xytext=(0, 8),
        textcoords="offset points",
        ha="center"
    )

save_chart("03_monthly_trend.png")


# --------------------------------------------------
# 4. DEPARTMENT RESOLUTION PERFORMANCE
# --------------------------------------------------

department_plot = departments.sort_values("resolution_rate")

plt.figure(figsize=(11, 6))

bars = plt.barh(
    department_plot["department_name"],
    department_plot["resolution_rate"],
    color=BLUE
)

plt.title("CivicTrack - Department Resolution Performance")
plt.xlabel("Resolution Rate (%)")
plt.ylabel("Department")
plt.xlim(0, 100)

for bar in bars:
    plt.text(
        bar.get_width() + 1,
        bar.get_y() + bar.get_height() / 2,
        f"{bar.get_width():.1f}%",
        va="center"
    )

save_chart("04_department_performance.png")


# --------------------------------------------------
# 5. AREA-WISE COMPLAINT DISTRIBUTION
# --------------------------------------------------

area_plot = areas.sort_values("total_complaints")

plt.figure(figsize=(10, 7))

bars = plt.barh(
    area_plot["area"],
    area_plot["total_complaints"],
    color=TEAL
)

plt.title("CivicTrack - Area-wise Complaint Distribution")
plt.xlabel("Number of Complaints")
plt.ylabel("Area")

for bar in bars:
    plt.text(
        bar.get_width() + 0.1,
        bar.get_y() + bar.get_height() / 2,
        int(bar.get_width()),
        va="center"
    )

save_chart("05_area_distribution.png")


# --------------------------------------------------
# 6. RESOLUTION TIME DISTRIBUTION
# --------------------------------------------------

resolution["resolution_hours"] = pd.to_numeric(
    resolution["resolution_hours"],
    errors="coerce"
)

plt.figure()

plt.hist(
    resolution["resolution_hours"],
    bins=10,
    color=PURPLE,
    edgecolor="white"
)

plt.title("CivicTrack - Complaint Resolution Time Distribution")
plt.xlabel("Resolution Time (Hours)")
plt.ylabel("Number of Complaints")
plt.grid(axis="y", alpha=0.2)

save_chart("06_resolution_time_distribution.png")


# --------------------------------------------------
# 7. CITIZEN FEEDBACK DISTRIBUTION
# --------------------------------------------------

rating_counts = (
    feedback["rating"]
    .value_counts()
    .sort_index()
)

plt.figure()

bars = plt.bar(
    rating_counts.index.astype(str),
    rating_counts.values,
    color=GREEN,
    width=0.6
)

plt.title("CivicTrack - Citizen Feedback Ratings")
plt.xlabel("Rating (1 to 5)")
plt.ylabel("Number of Feedback Records")
plt.xticks(["1", "2", "3", "4", "5"])

for bar in bars:
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        int(bar.get_height()),
        ha="center",
        va="bottom"
    )

save_chart("07_feedback_distribution.png")


# --------------------------------------------------
# 8. CURRENT STAFF WORKLOAD
# --------------------------------------------------

staff_plot = staff.sort_values(
    "current_assigned_complaints"
)

plt.figure(figsize=(10, 7))

bars = plt.barh(
    staff_plot["staff_name"],
    staff_plot["current_assigned_complaints"],
    color=ORANGE
)

plt.title("CivicTrack - Current Staff Workload")
plt.xlabel("Current Assigned Complaints")
plt.ylabel("Staff Member")

for bar in bars:
    plt.text(
        bar.get_width() + 0.05,
        bar.get_y() + bar.get_height() / 2,
        int(bar.get_width()),
        va="center"
    )

save_chart("08_staff_workload.png")


print("\n======================================")
print("EDA VISUALIZATIONS COMPLETED")
print("======================================")
print("Total charts generated: 8")
print("Chart folder:", CHART_DIR)
