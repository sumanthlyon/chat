from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.schema.user import (
    UserCreate,
    UserLogin
)

from app.services.auth_service import (
    create_user,
    authenticate_user
)

from app.core.jwt_handler import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    new_user = create_user(
        db,
        user.username,
        user.email,
        user.password
    )

    return {
        "message": "User created successfully",
        "user_id": new_user.id
    }


@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    print("LOGIN EMAIL:", user.email)

    authenticated_user = authenticate_user(
        db,
        user.email,
        user.password
    )

    print("USER FOUND:", authenticated_user)

    if not authenticated_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        {
            "sub": str(authenticated_user.id),
            "email": authenticated_user.email,
            "username": authenticated_user.username
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": authenticated_user.id,
            "username": authenticated_user.username,
            "email": authenticated_user.email
        }
    }