from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    StreamingMessageDTO,
    StreamState,
)
from luminary.chat.application.interfaces.usecases.command.send_message_use_case import (
    MessageDTO,
)
from luminary.chat.domain.enums import Author, MessageStatus


class MessageResponse(BaseModel):
    message_id: UUID
    chat_id: UUID
    content: str
    author: Author
    status: MessageStatus
    tokens: int | None
    created_at: datetime

    @classmethod
    def from_dto(cls, dto: MessageDTO) -> Self:
        return cls(
            message_id=dto.message_id,
            chat_id=dto.chat_id,
            content=dto.content,
            author=dto.author,
            status=dto.status,
            tokens=dto.tokens,
            created_at=dto.created_at.value,
        )


class StreamingMessageResponse(BaseModel):
    message_id: UUID
    state: StreamState
    content: str
    author: Author
    status: MessageStatus

    @classmethod
    def from_dto(cls, dto: StreamingMessageDTO) -> Self:
        return cls(
            message_id=dto.message_id,
            state=dto.state,
            content=dto.content,
            author=dto.author,
            status=dto.status,
        )
