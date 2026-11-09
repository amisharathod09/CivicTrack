
from pydantic import BaseModel, Field


# Data received when a citizen submits a complaint
class ComplaintCreate(BaseModel):

    category_id: int = Field(gt=0)

    location_id: int = Field(gt=0)

    title: str = Field(min_length=5, max_length=150)

    description: str = Field(min_length=10)


# Data returned after complaint creation
class ComplaintResponse(BaseModel):

    request_id: int
    citizen_id: int
    category_id: int
    location_id: int
    title: str
    description: str
    priority: str
    status: str

    model_config = {
        "from_attributes": True
    }


# Data received when staff updates a complaint status
class StaffStatusUpdate(BaseModel):

    status: str = Field(
        pattern="^(In Progress|Resolved)$"
    )

    change_note: str = Field(
        min_length=10,
        max_length=500
    )
