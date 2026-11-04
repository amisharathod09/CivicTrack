from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category


router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get("")
def get_categories(db: Session = Depends(get_db)):

    categories = db.scalars(
        select(Category)
    ).all()

    return [
        {
            "category_id": category.category_id,
            "department_id": category.department_id,
            "category_name": category.category_name,
            "description": category.description,
            "default_priority": category.default_priority,
            "is_active": category.is_active
        }
        for category in categories
    ]