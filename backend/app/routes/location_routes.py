from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Location


router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)


@router.get("")
def get_locations(db: Session = Depends(get_db)):

    locations = db.scalars(
        select(Location)
    ).all()

    return [
        {
            "location_id": location.location_id,
            "area": location.area,
            "city": location.city,
            "state": location.state,
            "pin_code": location.pin_code,
            "full_address": location.full_address
        }
        for location in locations
    ]