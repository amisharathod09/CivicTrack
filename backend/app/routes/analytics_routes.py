
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.auth_dependencies import require_roles
from app.services.analytics_service import (
    get_complaint_overview,
    get_complaint_trends,
    get_category_analytics,
    get_department_analytics,
    get_staff_workload_analytics,
    get_sla_performance_analytics,
    get_priority_analytics,
    get_resolution_time_analytics,
    get_feedback_analytics
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# Get complaint overview analytics (Admin only)
@router.get("/overview")
def complaint_overview(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    return get_complaint_overview(db)


# Get monthly complaint trends (Admin only)
@router.get("/trends")
def complaint_trends(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    return get_complaint_trends(db)


# Get complaint category analytics (Admin only)
@router.get("/categories")
def category_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    return get_category_analytics(db)

@router.get("/departments")
def department_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    return get_department_analytics(db)

@router.get("/staff-workload")
def staff_workload_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    return get_staff_workload_analytics(db)

@router.get("/sla-performance")
def sla_performance_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    return get_sla_performance_analytics(db)

@router.get("/priority")
def priority_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    return get_priority_analytics(db)

@router.get("/resolution-time")
def resolution_time_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    return get_resolution_time_analytics(db)

@router.get("/feedback")
def feedback_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    return get_feedback_analytics(db)