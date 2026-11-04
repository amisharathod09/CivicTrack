from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth_schema import UserRegister, UserLogin
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