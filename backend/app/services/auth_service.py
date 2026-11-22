from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.department import Department
from app.schemas.auth_schema import UserRegister, UserLogin, StaffCreate,StaffUpdate
from app.services.security_service import hash_password, verify_password
from app.services.jwt_service import create_access_token


# Register a new citizen
def register_citizen(user_data: UserRegister, db: Session):

    existing_user = db.scalar(
        select(User).where(User.email == user_data.email)
    )

    if existing_user:
        return None

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        phone=user_data.phone,
        role="citizen"
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except IntegrityError:
        db.rollback()
        return None

    except Exception:
        db.rollback()
        raise

# Create a new staff member (Admin only)
def create_staff(user_data: StaffCreate, db: Session):

    # Check whether email already exists
    existing_user = db.scalar(
        select(User).where(User.email == user_data.email)
    )

    if existing_user:
        return None

    # Check whether department exists and is active
    department = db.scalar(
        select(Department).where(
            Department.department_id == user_data.department_id,
            Department.is_active.is_(True)
        )
    )

    if not department:
        raise ValueError("Invalid or inactive department.")

    new_staff = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        phone=user_data.phone,
        role="staff",
        department_id=user_data.department_id,
        is_active=True
    )

    try:
        db.add(new_staff)
        db.commit()
        db.refresh(new_staff)

        return new_staff

    except IntegrityError:
        db.rollback()
        return None

    except Exception:
        db.rollback()
        raise

# Authenticate an existing user
def authenticate_user(user_data: UserLogin, db: Session):

    user = db.scalar(
        select(User).where(User.email == user_data.email)
    )

    if not user:
        return None

    if not user.is_active:
        return None

    if not verify_password(
        user_data.password,
        user.password_hash
    ):
        return None

    access_token = create_access_token({
        "user_id": user.user_id,
        "role": user.role
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

def update_staff(user_id: int, user_data: StaffUpdate, db: Session):

    staff = db.scalar(
        select(User).where(
            User.user_id == user_id,
            User.role == "staff"
        )
    )

    if not staff:
        return None

    department = db.scalar(
        select(Department).where(
            Department.department_id == user_data.department_id,
            Department.is_active.is_(True)
        )
    )

    if not department:
        raise ValueError("Invalid or inactive department.")

    staff.full_name = user_data.full_name
    staff.phone = user_data.phone
    staff.department_id = user_data.department_id

    try:
        db.commit()
        db.refresh(staff)
        return staff

    except Exception:
        db.rollback()
        raise

# Activate or deactivate a staff member (Admin only)
def update_staff_status(user_id: int, is_active: bool, db: Session):

    staff = db.scalar(
        select(User).where(
            User.user_id == user_id,
            User.role == "staff"
        )
    )

    if not staff:
        return None

    staff.is_active = is_active

    try:
        db.commit()
        db.refresh(staff)
        return staff

    except Exception:
        db.rollback()
        raise