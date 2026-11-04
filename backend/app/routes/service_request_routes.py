from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ServiceRequest


router = APIRouter(
    prefix="/service-requests",
    tags=["Service Requests"]
)


@router.get("")
def get_service_requests(db: Session = Depends(get_db)):

    service_requests = db.scalars(
        select(ServiceRequest)
    ).all()

    return [
        {
            "request_id": request.request_id,
            "citizen_id": request.citizen_id,
            "category_id": request.category_id,
            "location_id": request.location_id,
            "title": request.title,
            "description": request.description,
            "priority": request.priority,
            "status": request.status,
            "sla_due_at": request.sla_due_at,
            "created_at": request.created_at,
            "updated_at": request.updated_at,
            "resolved_at": request.resolved_at
        }
        for request in service_requests
    ]