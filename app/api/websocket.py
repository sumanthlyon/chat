from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.jwt_handler import decode_access_token
from app.database.connection import SessionLocal
from app.database.models import Message, User
from app.schema.message import MessageCreate
from app.services.connection_manager import manager


router = APIRouter(
    tags=["WebSocket Chat"],
)


def get_user_from_token(
    token: str,
    db: Session,
) -> User | None:
    payload = decode_access_token(token)

    print("DECODED TOKEN:", payload)

    if payload is None:
        return None

    user_id_value = payload.get("sub")

    if user_id_value is None:
        return None

    try:
        user_id = int(user_id_value)

    except (TypeError, ValueError):
        return None

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    return user


@router.websocket("/ws/chat")
async def chat_websocket(
    websocket: WebSocket,
):
    token = websocket.query_params.get(
        "token"
    )

    print(
        "WEBSOCKET CONNECTION ATTEMPT"
    )

    if not token:
        await websocket.close(
            code=status.WS_1008_POLICY_VIOLATION,
            reason=(
                "Authentication token is required"
            ),
        )

        return

    db = SessionLocal()

    current_user = None

    try:
        current_user = (
            get_user_from_token(
                token,
                db,
            )
        )

        if current_user is None:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION,
                reason=(
                    "Invalid or expired token"
                ),
            )

            return

        print(
            "WEBSOCKET AUTHENTICATED USER:",
            current_user.id,
        )

        await manager.connect(
            current_user.id,
            websocket,
        )

        print(
            "WEBSOCKET CONNECTED"
        )

        await websocket.send_json(
            {
                "type": "connection",
                "message": (
                    "WebSocket connected successfully"
                ),
                "user_id": current_user.id,
            }
        )

        while True:
            incoming_data = (
                await websocket.receive_json()
            )

            print(
                "WEBSOCKET DATA RECEIVED:",
                incoming_data,
            )

            event_type = (
                incoming_data.get("type")
            )

            if event_type == "message":
                await process_message(
                    incoming_data=(
                        incoming_data
                    ),
                    current_user=(
                        current_user
                    ),
                    db=db,
                )

            elif event_type == "ping":
                await websocket.send_json(
                    {
                        "type": "pong",
                    }
                )

            else:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": (
                            "Unsupported event type"
                        ),
                    }
                )

    except WebSocketDisconnect:
        print(
            "WEBSOCKET DISCONNECTED"
        )

        if current_user is not None:
            manager.disconnect(
                current_user.id,
                websocket,
            )

    except Exception as error:
        print(
            "WEBSOCKET SERVER ERROR:",
            repr(error),
        )

        if current_user is not None:
            manager.disconnect(
                current_user.id,
                websocket,
            )

    finally:
        db.close()


async def process_message(
    incoming_data: dict,
    current_user: User,
    db: Session,
):
    print(
        "\n--- PROCESSING ENCRYPTED MESSAGE ---"
    )

    print(
        "Sender ID:",
        current_user.id,
    )

    print(
        "Receiver ID:",
        incoming_data.get(
            "receiver_id"
        ),
    )

    try:
        message_data = MessageCreate(
            receiver_id=(
                incoming_data.get(
                    "receiver_id"
                )
            ),

            encrypted_message=(
                incoming_data.get(
                    "encrypted_message",
                    "",
                )
            ),

            encrypted_aes_key_receiver=(
                incoming_data.get(
                    "encrypted_aes_key_receiver",
                    "",
                )
            ),

            encrypted_aes_key_sender=(
                incoming_data.get(
                    "encrypted_aes_key_sender",
                    "",
                )
            ),

            iv=(
                incoming_data.get(
                    "iv",
                    "",
                )
            ),
        )

    except ValidationError as error:
        print(
            "MESSAGE VALIDATION ERROR:",
            error,
        )

        await manager.send_to_user(
            current_user.id,
            {
                "type": "error",
                "message": (
                    "Invalid encrypted message data"
                ),
            },
        )

        return

    receiver = (
        db.query(User)
        .filter(
            User.id
            == message_data.receiver_id
        )
        .first()
    )

    if receiver is None:
        await manager.send_to_user(
            current_user.id,
            {
                "type": "error",
                "message": (
                    "Receiver does not exist"
                ),
            },
        )

        return

    if receiver.id == current_user.id:
        await manager.send_to_user(
            current_user.id,
            {
                "type": "error",
                "message": (
                    "You cannot send a message "
                    "to yourself"
                ),
            },
        )

        return

    new_message = Message(
        sender_id=(
            current_user.id
        ),

        receiver_id=(
            receiver.id
        ),

        encrypted_message=(
            message_data.encrypted_message
        ),

        encrypted_aes_key_receiver=(
            message_data
            .encrypted_aes_key_receiver
        ),

        encrypted_aes_key_sender=(
            message_data
            .encrypted_aes_key_sender
        ),

        iv=(
            message_data.iv
        ),
    )

    db.add(
        new_message
    )

    try:
        db.commit()

        db.refresh(
            new_message
        )

        print(
            "ENCRYPTED MESSAGE SAVED"
        )

        print(
            "Message ID:",
            new_message.id,
        )

    except Exception as error:
        db.rollback()

        print(
            "DATABASE ERROR:",
            repr(error),
        )

        await manager.send_to_user(
            current_user.id,
            {
                "type": "error",
                "message": (
                    "Encrypted message "
                    "could not be saved"
                ),
            },
        )

        return

    response_data = {
        "type": "message",

        "message": {
            "id":
                new_message.id,

            "sender_id":
                new_message.sender_id,

            "receiver_id":
                new_message.receiver_id,

            "encrypted_message":
                new_message.encrypted_message,

            "encrypted_aes_key_receiver":
                new_message
                .encrypted_aes_key_receiver,

            "encrypted_aes_key_sender":
                new_message
                .encrypted_aes_key_sender,

            "iv":
                new_message.iv,

            "created_at":
                new_message.created_at
                .isoformat(),
        },
    }

    # Send encrypted payload
    # to the receiver.
    await manager.send_to_user(
        receiver.id,
        response_data,
    )

    # Also send the same encrypted
    # payload back to the sender.
    await manager.send_to_user(
        current_user.id,
        response_data,
    )

    print(
        "--- ENCRYPTED MESSAGE COMPLETE ---\n"
    )