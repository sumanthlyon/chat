# from fastapi import (
#     APIRouter,
#     Depends,
#     HTTPException,
#     Query,
#     status
# )

# from sqlalchemy import and_, or_
# from sqlalchemy.orm import Session
# from app.core.auth_dependencies import (
#     get_current_user,
# )
# from app.database.dependencies import get_db
# from app.database.models import Message, User
# from app.schema.message import MessageResponse

# router = APIRouter(
#     prefix="/messages",
#     tags=["Messages"],
# )

# @router.get(
#         "/conversation/{other_user_id}",
#         response_model = list[MessageResponse]
# )

# def get_conversation(
#     other_user_id: int,
#     limit: int = Query(
#         default= 50,
#         ge =1,
#         le = 100,
#     ),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(
#         get_current_user
#     ),

# ):

#     other_user = (
#         db.query(User)
#         .filter(User.id == other_user_id)
#         .first()
#     )

#     if other_user is None:
#         raise HTTPException(
#             status_code=(
#                 status.HTTP_404_NOT_FOUND
#             ),
#             detail="User not found"
#         )

#     messages = (
#         db.query(Message)
#         .filter(
#            or_(
#                and_(
#                    Message.sender_id == current_user.id,
#                    Message.receiver_id == other_user_id,
#                ),
#                and_(
#                    Message.sender_id == other_user_id,
#                    Message.receiver_id == current_user.id,
#                ),
#            ) 
#         )

#         .order_by(
#             Message.created_at.desc()
#         )
#         .limit(limit)
#         .all()

#     )

#     messages.reverse()

#     return messages


# # @router.get("/")
# # def messages_status():
# #     return {
# #         "message": "Real-time messaging is active",
# #         "storage_enabled": False,
# #         "receiver_selection_enabled": False,
# #         "mode": "WebSocket broadcast test",
# #     }

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.database.dependencies import get_db
from app.database.models import Message, User

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
)


@router.get("/conversation/{other_user_id}")
def get_conversation(
    other_user_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    other_user = (
        db.query(User)
        .filter(User.id == other_user_id)
        .first()
    )

    if other_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    messages = (
        db.query(Message)
        .filter(
            or_(
                and_(
                    Message.sender_id == current_user.id,
                    Message.receiver_id == other_user_id,
                ),
                and_(
                    Message.sender_id == other_user_id,
                    Message.receiver_id == current_user.id,
                ),
            )
        )
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )

    messages.reverse()

    return [
        {
        "id": item.id,

        "sender_id":
            item.sender_id,

        "receiver_id":
            item.receiver_id,

        "encrypted_message":
            item.encrypted_message,

        "encrypted_aes_key_receiver":
            item.encrypted_aes_key_receiver,

        "encrypted_aes_key_sender":
            item.encrypted_aes_key_sender,

        "iv":
            item.iv,

        "created_at":
            item.created_at,
    }

    for item in messages
    ]