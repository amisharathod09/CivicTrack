from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    phone: str | None = Field(default=None, max_length=15)


class UserLogin(BaseModel):
    email: EmailStr
    password: str