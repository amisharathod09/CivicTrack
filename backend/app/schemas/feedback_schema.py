from pydantic import BaseModel, Field


# Schema for submitting feedback
class FeedbackCreate(BaseModel):
    request_id: int = Field(gt=0)
    rating: int = Field(ge=1, le=5)
    comments: str | None = None


# Schema for editing existing feedback
class FeedbackUpdate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comments: str | None = None


# Schema for returning feedback details
class FeedbackResponse(BaseModel):
    feedback_id: int
    request_id: int
    citizen_id: int
    rating: int
    comments: str | None
    model_config = {"from_attributes": True}