from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth_schema import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    StaffCreate,
    StaffUpdate,
    StaffStatusUpdate
)
from app.services.auth_service import (
    register_citizen,
    authenticate_user,
    create_staff,
    update_staff,
    update_staff_status
)
from app.utils.auth_dependencies import get_current_user
from app.models.user import User
from app.utils.auth_dependencies import require_roles
from sqlalchemy import select

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
# Admin-only: Get all active staff members
@router.get("/staff")
def get_active_staff(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    staff_members = db.scalars(
        select(User).where(
            User.role == "staff",
            User.is_active.is_(True)
        ).order_by(User.full_name)
    ).all()

    return [
    {
        "user_id": staff.user_id,
        "full_name": staff.full_name,
        "email": staff.email,
        "phone": staff.phone,
        "department_id": staff.department_id
    }
    for staff in staff_members
]
# Admin-only: Create a new staff member
@router.post(
    "/staff",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_staff_member(
    staff_data: StaffCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    try:
        new_staff = create_staff(staff_data, db)

        if new_staff is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists."
            )

        return new_staff

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )

# Update an existing staff member (Admin only)
@router.put("/staff/{user_id}", response_model=UserResponse)
def update_staff_member(
    user_id: int,
    staff_data: StaffUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    try:
        updated_staff = update_staff(user_id, staff_data, db)

        if updated_staff is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Staff member not found."
            )

        return updated_staff

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )

# Admin-only: Get all staff members (active and inactive)
@router.get("/staff/manage")
def get_all_staff_for_management(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    staff_members = db.scalars(
        select(User).where(
            User.role == "staff"
        ).order_by(User.full_name)
    ).all()

    return [
        {
            "user_id": staff.user_id,
            "full_name": staff.full_name,
            "email": staff.email,
            "phone": staff.phone,
            "department_id": staff.department_id,
            "is_active": staff.is_active
        }
        for staff in staff_members
    ]


# Admin-only: Activate or deactivate a staff member
@router.patch("/staff/{user_id}/status")
def change_staff_status(
    user_id: int,
    status_data: StaffStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    updated_staff = update_staff_status(
        user_id,
        status_data.is_active,
        db
    )

    if updated_staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found."
        )

    return {
        "message": (
            "Staff member activated successfully."
            if updated_staff.is_active
            else "Staff member deactivated successfully."
        ),
        "user_id": updated_staff.user_id,
        "is_active": updated_staff.is_active
    }