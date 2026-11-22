from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    phone: str | None = Field(default=None, max_length=15)

class StaffCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    phone: str | None = Field(default=None, max_length=15)
    department_id: int = Field(gt=0)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    phone: str | None
    role: str
    department_id: int | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class StaffUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: str | None = Field(default=None, max_length=15)
    department_id: int = Field(gt=0)

class StaffStatusUpdate(BaseModel):
    is_active: bool