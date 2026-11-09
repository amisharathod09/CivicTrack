
from pydantic import BaseModel, Field


# Data received when an admin assigns a complaint
class AssignmentCreate(BaseModel):

    request_id: int = Field(gt=0)

    staff_id: int = Field(gt=0)

    notes: str | None = Field(
        default=None,
        max_length=500
    )
