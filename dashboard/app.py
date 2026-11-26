
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="CivicTrack | Analytics Dashboard",
    page_icon="🏙️",
    layout="wide"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "analytics" / "outputs"


# --------------------------------------------------
# 2. LOAD ANALYTICS DATA
# --------------------------------------------------

@st.cache_data
def load_data():

    files = {
        "complaints": "cleaned_complaints.csv",
        "resolution": "cleaned_resolution_metrics.csv",
        "departments": "cleaned_department_summary.csv",
        "monthly": "cleaned_monthly_trends.csv",
        "staff": "cleaned_staff_workload.csv",
        "feedback": "cleaned_feedback_ratings.csv",
        "priority": "priority_analysis.csv",
        "status": "status_analysis.csv",
        "department_performance": "department_performance.csv",
        "area": "area_analysis.csv",
        "monthly_analysis": "monthly_analysis.csv",
        "feedback_analysis": "feedback_analysis.csv",
    }

    data = {}

    for key, filename in files.items():

        file_path = OUTPUT_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Required file not found: {file_path}"
            )

        data[key] = pd.read_csv(file_path)

    # Convert date columns
    for dataset, column in [
        ("complaints", "created_at"),
        ("complaints", "resolved_at"),
        ("resolution", "created_at"),
        ("resolution", "resolved_at"),
        ("feedback", "created_at"),
    ]:
        data[dataset][column] = pd.to_datetime(
            data[dataset][column],
            errors="coerce"
        )

    # Convert numeric columns
    for dataset, column in [
        ("complaints", "request_id"),
        ("resolution", "request_id"),
        ("resolution", "resolution_hours"),
        ("feedback", "request_id"),
        ("feedback", "rating"),
        ("staff", "current_assigned_complaints"),
    ]:
        data[dataset][column] = pd.to_numeric(
            data[dataset][column],
            errors="coerce"
        )

    return data


# --------------------------------------------------
# 3. LOAD DATA SAFELY
# --------------------------------------------------

try:
    data = load_data()

except Exception as error:
    st.error(f"Unable to load analytics data: {error}")
    st.stop()


complaints = data["complaints"].copy()
resolution = data["resolution"].copy()
departments = data["departments"].copy()
monthly = data["monthly"].copy()
staff = data["staff"].copy()
feedback = data["feedback"].copy()


# --------------------------------------------------
# 4. DASHBOARD HEADER
# --------------------------------------------------

st.title("🏙️ CivicTrack Analytics Dashboard")

st.write(
    "Smart Public Service Request & Operations Analytics Platform"
)

st.caption(
    "Monitor public complaints, service performance, "
    "department workload and citizen feedback."
)

st.divider()


# --------------------------------------------------
# 5. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.title("Dashboard Filters")

st.sidebar.caption("Filter the dashboard data below.")

priorities = sorted(
    complaints["priority"].dropna().unique().tolist()
)

statuses = sorted(
    complaints["status"].dropna().unique().tolist()
)

department_options = sorted(
    complaints["department_name"].dropna().unique().tolist()
)

area_options = sorted(
    complaints["area"].dropna().unique().tolist()
)

selected_priorities = st.sidebar.multiselect(
    "Priority",
    priorities,
    default=priorities
)

selected_statuses = st.sidebar.multiselect(
    "Complaint Status",
    statuses,
    default=statuses
)

selected_departments = st.sidebar.multiselect(
    "Department",
    department_options,
    default=department_options
)

selected_areas = st.sidebar.multiselect(
    "Area",
    area_options,
    default=area_options
)

# Date range
valid_dates = complaints["created_at"].dropna()

if not valid_dates.empty:

    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    selected_dates = st.sidebar.date_input(
        "Complaint Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

else:
    selected_dates = None


# --------------------------------------------------
# 6. APPLY FILTERS
# --------------------------------------------------

filtered = complaints.copy()

filtered = filtered[
    filtered["priority"].isin(selected_priorities)
    & filtered["status"].isin(selected_statuses)
    & filtered["department_name"].isin(selected_departments)
    & filtered["area"].isin(selected_areas)
]

if selected_dates and len(selected_dates) == 2:

    start_date, end_date = selected_dates

    filtered = filtered[
        filtered["created_at"].dt.date.between(
            start_date,
            end_date
        )
    ]


# Related resolution records
filtered_ids = filtered["request_id"].dropna().unique()

filtered_resolution = resolution[
    resolution["request_id"].isin(filtered_ids)
].copy()

# Related feedback records
filtered_feedback = feedback[
    feedback["request_id"].isin(filtered_ids)
].copy()


# --------------------------------------------------
# 7. CALCULATE KPIs
# --------------------------------------------------

total_complaints = len(filtered)

completed_statuses = ["Resolved", "Closed"]

active_statuses = [
    "Submitted",
    "Assigned",
    "In Progress"
]

completed_complaints = filtered[
    filtered["status"].isin(completed_statuses)
].shape[0]

active_complaints = filtered[
    filtered["status"].isin(active_statuses)
].shape[0]

cancelled_complaints = filtered[
    filtered["status"] == "Cancelled"
].shape[0]

resolution_rate = (
    completed_complaints / total_complaints * 100
    if total_complaints > 0
    else 0
)

average_resolution = (
    filtered_resolution["resolution_hours"].mean()
    if not filtered_resolution.empty
    else 0
)

average_rating = (
    filtered_feedback["rating"].mean()
    if not filtered_feedback.empty
    else 0
)


# --------------------------------------------------
# 8. KPI CARDS
# --------------------------------------------------

st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Complaints",
    f"{total_complaints:,}"
)

col2.metric(
    "Resolved / Closed",
    f"{completed_complaints:,}"
)

col3.metric(
    "Active Complaints",
    f"{active_complaints:,}"
)

col4.metric(
    "Cancelled Complaints",
    f"{cancelled_complaints:,}"
)

col5, col6, col7 = st.columns(3)

col5.metric(
    "Resolution Rate",
    f"{resolution_rate:.2f}%"
)

col6.metric(
    "Average Resolution Time",
    f"{average_resolution:.2f} hours"
)

col7.metric(
    "Average Feedback Rating",
    f"{average_rating:.2f} / 5"
)

st.divider()


# --------------------------------------------------
# 9. OVERVIEW CHARTS
# --------------------------------------------------

st.subheader("Complaint Overview")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:

    status_data = (
        filtered.groupby("status")
        .size()
        .reset_index(name="total_complaints")
    )

    if not status_data.empty:

        fig_status = px.pie(
            status_data,
            names="status",
            values="total_complaints",
            hole=0.45,
            title="Complaint Status Distribution"
        )

        st.plotly_chart(
            fig_status,
            width="stretch"
        )

    else:
        st.info("No status data available.")


with chart_col2:

    priority_data = (
        filtered.groupby("priority")
        .size()
        .reset_index(name="total_complaints")
    )

    if not priority_data.empty:

        fig_priority = px.bar(
            priority_data,
            x="priority",
            y="total_complaints",
            color="priority",
            title="Complaints by Priority",
            text_auto=True
        )

        st.plotly_chart(
            fig_priority,
            width="stretch"
        )

    else:
        st.info("No priority data available.")



# --------------------------------------------------
# 10. MONTHLY COMPLAINT TREND
# --------------------------------------------------

st.subheader("Monthly Complaint Trends")

if not filtered.empty:

    trend_data = filtered.copy()

    trend_data["complaint_period"] = (
        trend_data["created_at"].dt.to_period("M")
    )

    trend_data = (
        trend_data.groupby("complaint_period")
        .size()
        .rename("total_complaints")
    )

    # Create a complete monthly timeline.
    # Missing months remain NaN, not zero.
    all_months = pd.period_range(
        start=trend_data.index.min(),
        end=trend_data.index.max(),
        freq="M"
    )

    trend_data = trend_data.reindex(all_months)

    chart_data = trend_data.rename_axis(
        "complaint_period"
    ).reset_index()

    chart_data["complaint_period"] = (
        chart_data["complaint_period"].astype(str)
    )

    fig_monthly = px.line(
        chart_data,
        x="complaint_period",
        y="total_complaints",
        markers=True,
        title="Monthly Complaint Submission Trend"
    )

    fig_monthly.update_traces(
        connectgaps=False
    )

    st.plotly_chart(
        fig_monthly,
        width="stretch"
    )

    st.caption(
        "Gaps indicate months with no recorded complaint data. "
        "They should not be interpreted as zero complaints."
    )

else:
    st.info("No monthly trend data available.")


# --------------------------------------------------
# 11. DEPARTMENT PERFORMANCE
# --------------------------------------------------

st.subheader("Department Performance")

if not filtered.empty:

    department_data = (
        filtered.groupby("department_name")
        .agg(
            total_complaints=("request_id", "count"),
            completed_complaints=(
                "status",
                lambda values: values.isin(completed_statuses).sum()
            )
        )
        .reset_index()
    )

    fig_department = px.bar(
        department_data,
        x="department_name",
        y="total_complaints",
        color="department_name",
        text_auto=True,
        title="Complaints by Department"
    )

    st.plotly_chart(
        fig_department,
        width="stretch"
    )

    st.dataframe(
        department_data,
        width="stretch",
        hide_index=True
    )

else:
    st.info("No department data available.")


# --------------------------------------------------
# 12. AREA-WISE ANALYSIS
# --------------------------------------------------

st.subheader("Area-wise Complaint Analysis")

if not filtered.empty:

    area_data = (
        filtered.groupby("area")
        .size()
        .reset_index(name="total_complaints")
        .sort_values("total_complaints", ascending=False)
    )

    fig_area = px.bar(
        area_data,
        x="area",
        y="total_complaints",
        color="total_complaints",
        title="Complaints by Area",
        text_auto=True
    )

    st.plotly_chart(
        fig_area,
        width="stretch"
    )

else:
    st.info("No area data available.")


st.divider()


# --------------------------------------------------
# 12A. COMPLAINT CATEGORY ANALYSIS
# --------------------------------------------------

st.divider()

st.subheader("Complaint Category Analysis")

st.caption(
    "Understand which types of public-service complaints "
    "are reported most frequently."
)

if not filtered.empty:

    category_data = (
        filtered.groupby("category_name")
        .size()
        .reset_index(name="total_complaints")
        .sort_values(
            "total_complaints",
            ascending=True
        )
    )

    fig_category = px.bar(
        category_data,
        x="total_complaints",
        y="category_name",
        orientation="h",
        text="total_complaints",
        title="Complaints by Category"
    )

    fig_category.update_layout(
        yaxis_title="Complaint Category",
        xaxis_title="Number of Complaints",
        showlegend=False
    )

    st.plotly_chart(
        fig_category,
        width="stretch"
    )

else:
    st.info("No complaint category data available.")


# --------------------------------------------------
# 12B. DEPARTMENT RESOLUTION PERFORMANCE
# --------------------------------------------------

st.divider()

st.subheader("Department Resolution Performance")

st.caption(
    "Compare complaint completion rates across departments."
)

if not filtered.empty:

    department_resolution = (
        filtered.groupby("department_name")
        .agg(
            total_complaints=("request_id", "count"),
            completed_complaints=(
                "status",
                lambda values: values.isin(
                    ["Resolved", "Closed"]
                ).sum()
            ),
            cancelled_complaints=(
                "status",
                lambda values: (values == "Cancelled").sum()
            )
        )
        .reset_index()
    )

    department_resolution["resolution_rate"] = (
        department_resolution["completed_complaints"]
        / department_resolution["total_complaints"]
        * 100
    )

    department_resolution = department_resolution.sort_values(
        "resolution_rate",
        ascending=True
    )

    fig_resolution = px.bar(
        department_resolution,
        x="resolution_rate",
        y="department_name",
        orientation="h",
        text=department_resolution["resolution_rate"].map(
            lambda value: f"{value:.2f}%"
        ),
        title="Department-wise Complaint Completion Rate"
    )

    fig_resolution.update_layout(
        xaxis_title="Completion Rate (%)",
        yaxis_title="Department",
        xaxis_range=[0, 100],
        showlegend=False
    )

    st.plotly_chart(
        fig_resolution,
        width="stretch"
    )

    st.dataframe(
        department_resolution,
        width="stretch",
        hide_index=True
    )

    st.caption(
        "Completion rate = Resolved and Closed complaints "
        "/ Total complaints × 100. Cancelled complaints "
        "remain in the denominator to match the existing "
        "CivicTrack analytics definition."
    )

else:
    st.info("No department performance data available.")


# --------------------------------------------------
# 12C. RESOLUTION TIME ANALYSIS
# --------------------------------------------------

st.divider()

st.subheader("Resolution Time Analysis")

st.caption(
    "Analyze how long completed complaints take to resolve "
    "and identify unusually long resolution times."
)

if not filtered_resolution.empty:

    resolution_data = filtered_resolution.copy()

    resolution_data["resolution_hours"] = pd.to_numeric(
        resolution_data["resolution_hours"],
        errors="coerce"
    )

    resolution_data = resolution_data.dropna(
        subset=["resolution_hours"]
    )

    if not resolution_data.empty:

        average_hours = resolution_data[
            "resolution_hours"
        ].mean()

        median_hours = resolution_data[
            "resolution_hours"
        ].median()

        outlier_flags = (
            resolution_data["resolution_time_outlier"]
            .astype(str)
            .str.lower()
            .isin(["true", "1", "yes"])
        )

        outlier_count = int(outlier_flags.sum())

        metric1, metric2, metric3 = st.columns(3)

        metric1.metric(
            "Average Resolution Time",
            f"{average_hours:.2f} hours"
        )

        metric2.metric(
            "Median Resolution Time",
            f"{median_hours:.2f} hours"
        )

        metric3.metric(
            "Unusually Long Resolutions",
            outlier_count
        )

        st.caption(
            "Resolution time metrics are calculated from "
            "completed complaints. The median is less affected "
            "by unusually long resolution times than the average."
        )

       
# Resolution time distribution
        st.markdown("#### Resolution Time Distribution")

        normal_data = resolution_data.loc[~outlier_flags].copy()
        outlier_data = resolution_data.loc[outlier_flags].copy()

        if not normal_data.empty:
            fig_distribution = px.histogram(
                normal_data,
                x="resolution_hours",
                nbins=15,
                title="Resolution Time Distribution (Without Flagged Outliers)",
                labels={
                    "resolution_hours": "Resolution Time (Hours)",
                    "count": "Number of Complaints"
                }
            )

            st.plotly_chart(
                fig_distribution,
                width="stretch"
            )
        else:
            st.info("No normal resolution-time records are available.")

        if not outlier_data.empty:
            st.markdown("#### Flagged Resolution Time Outliers")
            st.caption(
                "These records are shown separately so that unusually long "
                "resolution times do not compress the main distribution."
            )

            st.dataframe(
                outlier_data[
                    ["request_id", "category_name", "resolution_hours"]
                ],
                hide_index=True,
                width="stretch"
            )
        else:
            st.info("No resolution-time outliers were detected.")


        # Category-wise resolution time
        st.markdown("#### Average Resolution Time by Category")

        category_resolution = (
            resolution_data.groupby("category_name")
            .agg(
                average_hours=("resolution_hours", "mean"),
                median_hours=("resolution_hours", "median"),
                completed_complaints=("request_id", "count")
            )
            .reset_index()
            .sort_values(
                "average_hours",
                ascending=True
            )
        )

        fig_category_resolution = px.bar(
            category_resolution,
            x="average_hours",
            y="category_name",
            orientation="h",
            text=category_resolution["average_hours"].map(
                lambda value: f"{value:.2f} h"
            ),
            title="Average Resolution Time by Complaint Category"
        )

        fig_category_resolution.update_layout(
            xaxis_title="Average Resolution Time (Hours)",
            yaxis_title="Complaint Category",
            showlegend=False
        )

        st.plotly_chart(
            fig_category_resolution,
            width="stretch"
        )

        st.dataframe(
            category_resolution,
            width="stretch",
            hide_index=True
        )

    else:
        st.info("No valid resolution time records available.")

else:
    st.info(
        "No completed complaint resolution records "
        "available for the selected filters."
    )


# 12D. SLA MONITORING

st.markdown("---")
st.markdown("### SLA Monitoring")
st.caption(
    "Monitor complaint resolution against service-level deadlines "
    "and identify overdue complaints."
)

sla_file = (
    Path(__file__).resolve().parents[1]
    / "analytics"
    / "outputs"
    / "powerbi"
    / "sla_summary.csv"
)

if sla_file.exists():

    sla_data = pd.read_csv(sla_file)

    sla = sla_data.iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Eligible Complaints",
        int(sla["total_eligible_complaints"])
    )

    col2.metric(
        "Completed Complaints",
        int(sla["completed_complaints"])
    )

    col3.metric(
        "SLA Compliance Rate",
        f'{sla["sla_compliance_rate"]:.2f}%'
    )

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "Resolved Within SLA",
        int(sla["resolved_within_sla"])
    )

    col5.metric(
        "Resolved After SLA",
        int(sla["resolved_after_sla"])
    )

    col6.metric(
        "Active Overdue Complaints",
        int(sla["active_overdue_complaints"])
    )

    st.markdown("#### Completed Complaint SLA Performance")

    sla_chart_data = pd.DataFrame({
        "SLA Result": [
            "Resolved Within SLA",
            "Resolved After SLA"
        ],
        "Complaints": [
            int(sla["resolved_within_sla"]),
            int(sla["resolved_after_sla"])
        ]
    })

    fig_sla = px.pie(
        sla_chart_data,
        names="SLA Result",
        values="Complaints",
        hole=0.55,
        title="SLA Performance of Completed Complaints"
    )

    st.plotly_chart(
        fig_sla,
        width="stretch"
    )

    st.caption(
        "SLA compliance is calculated using completed complaints "
        "with available SLA deadlines. Active overdue complaints "
        "are reported separately."
    )

else:
    st.warning("SLA summary file was not found.")

# --------------------------------------------------
# 13. STAFF WORKLOAD
# --------------------------------------------------

st.subheader("Staff Workload Analysis")

st.caption(
    "Shows the number of complaints currently assigned "
    "to each staff member. The department filter applies here."
)

# Apply the selected department filter
staff_data = staff[
    staff["department_name"].isin(selected_departments)
].copy()

if not staff_data.empty:

    staff_data = staff_data.sort_values(
        "current_assigned_complaints",
        ascending=False
    )

    fig_staff = px.bar(
        staff_data,
        x="staff_name",
        y="current_assigned_complaints",
        color="department_name",
        title="Current Assigned Complaints by Staff",
        text_auto=True
    )

    st.plotly_chart(
        fig_staff,
        width="stretch"
    )

    st.dataframe(
        staff_data,
        width="stretch",
        hide_index=True
    )

else:
    st.info(
        "No staff workload data available for the selected departments."
    )


# --------------------------------------------------
# 14. CITIZEN FEEDBACK
# --------------------------------------------------

st.subheader("Citizen Feedback Analysis")

feedback_col1, feedback_col2 = st.columns(2)

with feedback_col1:

    if not filtered_feedback.empty:

        rating_data = (
            filtered_feedback.groupby("rating")
            .size()
            .reset_index(name="feedback_count")
        )

        fig_rating = px.bar(
            rating_data,
            x="rating",
            y="feedback_count",
            title="Citizen Feedback Ratings",
            text_auto=True
        )

        st.plotly_chart(
            fig_rating,
            width="stretch"
        )

    else:
        st.info("No feedback available for the selected filters.")


with feedback_col2:

    st.metric(
        "Total Feedback Responses",
        len(filtered_feedback)
    )

    st.metric(
        "Average Citizen Rating",
        f"{average_rating:.2f} / 5"
    )


# --------------------------------------------------
# 15. COMPLAINT DATA TABLE
# --------------------------------------------------

st.divider()

st.subheader("Complaint Records")

display_columns = [
    "request_id",
    "title",
    "category_name",
    "priority",
    "status",
    "department_name",
    "area",
    "created_at"
]

st.dataframe(
    filtered[display_columns].sort_values(
        "created_at",
        ascending=False
    ),
    width="stretch",
    hide_index=True
)


# --------------------------------------------------
# 16. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "CivicTrack | Smart Public Service Request "
    "& Operations Analytics Platform"
)

st.caption(
    "Analytics powered by Python, Pandas, Streamlit and Plotly."
)
