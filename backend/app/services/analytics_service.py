
from sqlalchemy import case,func,literal_column, select
from sqlalchemy.orm import Session

from app.models.service_request import ServiceRequest
from app.models.feedback import Feedback
from app.models.category import Category
from app.models.department import Department
from app.models.user import User
from app.models.assignment import Assignment

def get_complaint_overview(db: Session):

    # Count complaints by their current status
    status_counts = db.execute(
        select(
            ServiceRequest.status,
            func.count(ServiceRequest.request_id)
        ).group_by(ServiceRequest.status)
    ).all()

    counts = {
        status: count
        for status, count in status_counts
    }

    # Calculate total complaints
    total_complaints = sum(counts.values())

    # Count overdue active complaints
    overdue_complaints = db.scalar(
        select(func.count(ServiceRequest.request_id)).where(
            ServiceRequest.sla_due_at < func.now(),
            ServiceRequest.status.in_(
                ["Submitted", "Assigned", "In Progress"]
            )
        )
    ) or 0

    # Calculate average citizen feedback rating
    average_rating = db.scalar(
        select(func.avg(Feedback.rating))
    )

    return {
        "total_complaints": total_complaints,
        "submitted_complaints": counts.get("Submitted", 0),
        "assigned_complaints": counts.get("Assigned", 0),
        "in_progress_complaints": counts.get("In Progress", 0),
        "resolved_complaints": counts.get("Resolved", 0),
        "closed_complaints": counts.get("Closed", 0),
        "cancelled_complaints": counts.get("Cancelled", 0),
        "overdue_complaints": overdue_complaints,
        "average_feedback_rating": (
            round(float(average_rating), 2)
            if average_rating is not None
            else 0
        )
    }


def get_complaint_trends(db: Session):

    # Count complaints submitted each month
    submitted_trends = db.execute(
        select(
            func.date_format(
                ServiceRequest.created_at, "%Y-%m"
            ).label("month"),
            func.count(ServiceRequest.request_id).label("total")
        )
        .group_by("month")
        .order_by("month")
    ).all()

    # Count complaints resolved each month
    resolved_trends = db.execute(
        select(
            func.date_format(
                ServiceRequest.resolved_at, "%Y-%m"
            ).label("month"),
            func.count(ServiceRequest.request_id).label("total")
        )
        .where(ServiceRequest.resolved_at.is_not(None))
        .group_by("month")
        .order_by("month")
    ).all()

    # Convert database results into dictionaries
    submitted_data = {
        month: total
        for month, total in submitted_trends
    }

    resolved_data = {
        month: total
        for month, total in resolved_trends
    }

    # Combine all months from both datasets
    all_months = sorted(
        set(submitted_data) | set(resolved_data)
    )

    # Prepare monthly comparison
    trends = [
        {
            "month": month,
            "submitted": submitted_data.get(month, 0),
            "resolved": resolved_data.get(month, 0)
        }
        for month in all_months
    ]

    return {
        "total_months": len(trends),
        "trends": trends
    }


from app.models.category import Category


def get_category_analytics(db: Session):

    # Count complaints grouped by category
    category_results = db.execute(
        select(
            Category.category_id,
            Category.category_name,
            func.count(ServiceRequest.request_id).label("total"),
            func.sum(
                func.if_(
                    ServiceRequest.status.in_(
                        ["Resolved", "Closed"]
                    ),
                    1,
                    0
                )
            ).label("resolved"),
            func.sum(
                func.if_(
                    ServiceRequest.status.in_(
                        ["Submitted", "Assigned", "In Progress"]
                    ),
                    1,
                    0
                )
            ).label("active")
        )
        .join(
            ServiceRequest,
            ServiceRequest.category_id == Category.category_id
        )
        .group_by(
            Category.category_id,
            Category.category_name
        )
        .order_by(func.count(ServiceRequest.request_id).desc())
    ).all()

    # Calculate total complaints across categories
    total_complaints = sum(
        result.total for result in category_results
    )

    # Prepare category analytics
    categories = []

    for result in category_results:

        percentage = (
            (result.total / total_complaints) * 100
            if total_complaints > 0
            else 0
        )

        categories.append({
            "category_id": result.category_id,
            "category_name": result.category_name,
            "total_complaints": result.total,
            "resolved_complaints": result.resolved or 0,
            "active_complaints": result.active or 0,
            "percentage": round(percentage, 2)
        })

    return {
        "total_categories": len(categories),
        "total_complaints": total_complaints,
        "categories": categories
    }


from app.models.department import Department


def get_department_analytics(db: Session):

    department_results = db.execute(
        select(
            Department.department_id,
            Department.department_name,
            func.count(ServiceRequest.request_id).label("total"),
            func.sum(
                func.if_(
                    ServiceRequest.status.in_(["Resolved", "Closed"]),
                    1,
                    0
                )
            ).label("resolved"),
            func.sum(
                func.if_(
                    ServiceRequest.status.in_(
                        ["Submitted", "Assigned", "In Progress"]
                    ),
                    1,
                    0
                )
            ).label("active")
        )
        .join(
            Category,
            Category.department_id == Department.department_id
        )
        .join(
            ServiceRequest,
            ServiceRequest.category_id == Category.category_id
        )
        .group_by(
            Department.department_id,
            Department.department_name
        )
        .order_by(func.count(ServiceRequest.request_id).desc())
    ).all()

    departments = []

    for result in department_results:

        resolution_percentage = (
            (result.resolved / result.total) * 100
            if result.total > 0
            else 0
        )

        departments.append({
            "department_id": result.department_id,
            "department_name": result.department_name,
            "total_complaints": result.total,
            "resolved_complaints": result.resolved or 0,
            "active_complaints": result.active or 0,
            "resolution_percentage": round(
                resolution_percentage, 2
            )
        })

    return {
        "total_departments": len(departments),
        "departments": departments
    }


def get_staff_workload_analytics(db: Session):

    staff_results = db.execute(
        select(
            User.user_id,
            User.full_name,
            func.count(Assignment.assignment_id).label("assigned_complaints"),
            func.sum(
                func.if_(
                    ServiceRequest.status.in_(
                        ["Submitted", "Assigned", "In Progress"]
                    ),
                    1,
                    0
                )
            ).label("active_complaints")
        )
        .select_from(User)
        .join(
            Assignment,
            Assignment.staff_id == User.user_id
        )
        .join(
            ServiceRequest,
            ServiceRequest.request_id == Assignment.request_id
        )
        .where(
            User.role == "staff",
            Assignment.is_current == True
        )
        .group_by(
            User.user_id,
            User.full_name
        )
        .order_by(
            func.count(Assignment.assignment_id).desc()
        )
    ).all()

    staff_members = []

    for result in staff_results:
        staff_members.append({
            "staff_id": result.user_id,
            "staff_name": result.full_name,
            "assigned_complaints": result.assigned_complaints,
            "active_complaints": result.active_complaints or 0
        })

    return {
        "total_staff": len(staff_members),
        "total_current_assignments": sum(
            staff["assigned_complaints"] for staff in staff_members
        ),
        "staff_workload": staff_members
    }


def get_sla_performance_analytics(db: Session):

    # Total complaints with an SLA deadline
    total_with_sla = db.scalar(
        select(func.count(ServiceRequest.request_id)).where(
            ServiceRequest.sla_due_at.is_not(None)
        )
    ) or 0

    # Completed complaints with an SLA deadline
    completed_with_sla = db.scalar(
        select(func.count(ServiceRequest.request_id)).where(
            ServiceRequest.status.in_(["Resolved", "Closed"]),
            ServiceRequest.sla_due_at.is_not(None),
            ServiceRequest.resolved_at.is_not(None)
        )
    ) or 0

    # Completed within SLA
    resolved_within_sla = db.scalar(
        select(func.count(ServiceRequest.request_id)).where(
            ServiceRequest.status.in_(["Resolved", "Closed"]),
            ServiceRequest.sla_due_at.is_not(None),
            ServiceRequest.resolved_at.is_not(None),
            ServiceRequest.resolved_at <= ServiceRequest.sla_due_at
        )
    ) or 0

    # Completed after SLA deadline
    resolved_late = db.scalar(
        select(func.count(ServiceRequest.request_id)).where(
            ServiceRequest.status.in_(["Resolved", "Closed"]),
            ServiceRequest.sla_due_at.is_not(None),
            ServiceRequest.resolved_at.is_not(None),
            ServiceRequest.resolved_at > ServiceRequest.sla_due_at
        )
    ) or 0

    # Currently overdue active complaints
    overdue_active = db.scalar(
        select(func.count(ServiceRequest.request_id)).where(
            ServiceRequest.status.in_(
                ["Submitted", "Assigned", "In Progress"]
            ),
            ServiceRequest.sla_due_at.is_not(None),
            ServiceRequest.sla_due_at < func.now()
        )
    ) or 0

    # Calculate SLA compliance percentage
    compliance_percentage = (
        (resolved_within_sla / completed_with_sla) * 100
        if completed_with_sla > 0
        else 0
    )

    return {
        "total_complaints_with_sla": total_with_sla,
        "completed_complaints_with_sla": completed_with_sla,
        "resolved_within_sla": resolved_within_sla,
        "resolved_late": resolved_late,
        "overdue_active_complaints": overdue_active,
        "sla_compliance_percentage": round(
            compliance_percentage, 2
        )
    }

def get_priority_analytics(db: Session):

    priority_data = db.execute(
        select(
            ServiceRequest.priority,
            func.count(ServiceRequest.request_id).label("total_complaints"),

            func.sum(
                case(
                    (ServiceRequest.status.in_(["Resolved", "Closed"]), 1),
                    else_=0
                )
            ).label("resolved_complaints"),

            func.sum(
                case(
                    (
                        ServiceRequest.status.in_(
                            ["Submitted", "Assigned", "In Progress"]
                        ),
                        1
                    ),
                    else_=0
                )
            ).label("active_complaints")
        )
        .group_by(ServiceRequest.priority)
        .order_by(ServiceRequest.priority)
    ).all()

    total_complaints = sum(
        row.total_complaints for row in priority_data
    )

    priorities = []

    for row in priority_data:
        percentage = (
            (row.total_complaints / total_complaints) * 100
            if total_complaints > 0
            else 0
        )

        priorities.append({
            "priority": row.priority,
            "total_complaints": row.total_complaints,
            "resolved_complaints": row.resolved_complaints or 0,
            "active_complaints": row.active_complaints or 0,
            "percentage": round(percentage, 2)
        })

    return {
        "total_complaints": total_complaints,
        "total_priorities": len(priorities),
        "priorities": priorities
    }

def get_resolution_time_analytics(db: Session):

    # Calculate overall resolution time in seconds
    overall = db.execute(
        select(
            func.avg(
                func.timestampdiff(
                    literal_column("SECOND"),
                    ServiceRequest.created_at,
                    ServiceRequest.resolved_at
                )
            ).label("average_seconds"),

            func.min(
                func.timestampdiff(
                    literal_column("SECOND"),
                    ServiceRequest.created_at,
                    ServiceRequest.resolved_at
                )
            ).label("minimum_seconds"),

            func.max(
                func.timestampdiff(
                    literal_column("SECOND"),
                    ServiceRequest.created_at,
                    ServiceRequest.resolved_at
                )
            ).label("maximum_seconds"),

            func.count(ServiceRequest.request_id).label("total_resolved")
        ).where(
            ServiceRequest.status.in_(["Resolved", "Closed"]),
            ServiceRequest.resolved_at.is_not(None)
        )
    ).one()

    # Calculate resolution time grouped by priority
    priority_data = db.execute(
        select(
            ServiceRequest.priority,
            func.count(ServiceRequest.request_id).label("total_resolved"),
            func.avg(
                func.timestampdiff(
                    literal_column("SECOND"),
                    ServiceRequest.created_at,
                    ServiceRequest.resolved_at
                )
            ).label("average_seconds")
        )
        .where(
            ServiceRequest.status.in_(["Resolved", "Closed"]),
            ServiceRequest.resolved_at.is_not(None)
        )
        .group_by(ServiceRequest.priority)
        .order_by(ServiceRequest.priority)
    ).all()

    # Convert seconds into hours
    average_hours = (
        overall.average_seconds / 3600
        if overall.average_seconds is not None
        else 0
    )

    minimum_hours = (
        overall.minimum_seconds / 3600
        if overall.minimum_seconds is not None
        else 0
    )

    maximum_hours = (
        overall.maximum_seconds / 3600
        if overall.maximum_seconds is not None
        else 0
    )

    priority_breakdown = []

    for row in priority_data:
        average_priority_hours = (
            row.average_seconds / 3600
            if row.average_seconds is not None
            else 0
        )

        priority_breakdown.append({
            "priority": row.priority,
            "total_resolved": row.total_resolved,
            "average_resolution_hours": round(
                average_priority_hours, 2
            )
        })

    return {
        "total_resolved_complaints": overall.total_resolved,
        "average_resolution_hours": round(average_hours, 2),
        "minimum_resolution_hours": round(minimum_hours, 2),
        "maximum_resolution_hours": round(maximum_hours, 2),
        "priority_breakdown": priority_breakdown
    }

def get_feedback_analytics(db: Session):

    # Overall feedback statistics
    overall = db.execute(
        select(
            func.count(Feedback.feedback_id).label("total_feedback"),
            func.avg(Feedback.rating).label("average_rating"),
            func.min(Feedback.rating).label("minimum_rating"),
            func.max(Feedback.rating).label("maximum_rating")
        )
    ).one()

    # Count feedback by rating
    rating_data = db.execute(
        select(
            Feedback.rating,
            func.count(Feedback.feedback_id).label("total_feedback")
        )
        .group_by(Feedback.rating)
        .order_by(Feedback.rating)
    ).all()

    rating_distribution = []

    for row in rating_data:
        rating_distribution.append({
            "rating": row.rating,
            "total_feedback": row.total_feedback
        })

    return {
        "total_feedback": overall.total_feedback,
        "average_rating": round(
            float(overall.average_rating), 2
        ) if overall.average_rating is not None else 0,
        "minimum_rating": overall.minimum_rating or 0,
        "maximum_rating": overall.maximum_rating or 0,
        "rating_distribution": rating_distribution
    }