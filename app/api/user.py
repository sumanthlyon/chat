from pydantic import BaseModel, ConfigDict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.database.dependencies import get_db
from app.database.models import User
from app.services.connection_manager import manager

from app.schema.user import PublicKeyUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


class ChatUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_online: bool


@router.get("", response_model=list[ChatUserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    users = (
        db.query(User)
        .filter(User.id != current_user.id)
        .order_by(User.username.asc())
        .all()
    )

    return [
        ChatUserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_online=manager.is_online(user.id),
        )
        for user in users
    ]

@router.put("/public-key")
def update_public_key(
    key_data: PublicKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.public_key = key_data.public_key

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Public key saved successfully"
    }

@router.get("/{user_id}/public-key")
def get_public_key(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if not user.public_key:
        raise HTTPException(
            status_code=404,
            detail="User does not have a public key",
        )

    return {
        "user_id": user.id,
        "public_key": user.public_key,
    }