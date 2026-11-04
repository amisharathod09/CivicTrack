from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth_schema import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse
)
from app.services.auth_service import (
    register_citizen,
    authenticate_user
)
from app.utils.auth_dependencies import get_current_user
from app.models.user import User
from app.utils.auth_dependencies import require_roles

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# Citizen Registration
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(user_data: UserRegister, db: Session = Depends(get_db)):

    new_user = register_citizen(user_data, db)

    if new_user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists."
        )

    return new_user


# User Login
@router.post(
    "/login",
    response_model=TokenResponse
)
def login(user_data: UserLogin, db: Session = Depends(get_db)):

    token_data = authenticate_user(user_data, db)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    return token_data

# Get currently logged-in user's profile
@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

# Admin-only test endpoint
@router.get("/admin-check")
def admin_check(
    current_user: User = Depends(require_roles("admin"))
):
    return {
        "message": "Welcome Admin! Access granted.",
        "user_id": current_user.user_id,
        "role": current_user.role
    }


# Staff-only test endpoint
@router.get("/staff-check")
def staff_check(
    current_user: User = Depends(require_roles("staff"))
):
    return {
        "message": "Welcome Staff! Access granted.",
        "user_id": current_user.user_id,
        "role": current_user.role
    }