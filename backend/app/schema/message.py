from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    receiver_id: int

    encrypted_message: str = Field(
        min_length=1,
    )

    encrypted_aes_key_receiver: str = Field(
        min_length=1,
    )

    encrypted_aes_key_sender: str = Field(
        min_length=1,
    )

    iv: str = Field(
        min_length=1,
    )


class MessageResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    sender_id: int
    receiver_id: int

    encrypted_message: str
    encrypted_aes_key_receiver: str
    encrypted_aes_key_sender: str
    iv: str

    created_at: datetime