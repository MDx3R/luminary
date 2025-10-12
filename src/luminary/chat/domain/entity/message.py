from dataclasses import dataclass
from typing import Self
from uuid import UUID

from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime

from luminary.chat.domain.enums import ChatMessageAuthor


@dataclass
class ChatMessage:
    message_id: UUID
    chat_id: UUID
    model_id: UUID
    role: ChatMessageAuthor
    content: str
    edited_at: DateTime
    created_at: DateTime

    def __post_init__(self) -> None:
        if self.content.strip():
            raise InvariantViolationError("Message cannot be empty")

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        message_id: UUID,
        chat_id: UUID,
        model_id: UUID,
        role: ChatMessageAuthor,
        content: str,
        created_at: DateTime,
    ) -> Self:
        return cls(
            message_id=message_id,
            chat_id=chat_id,
            model_id=model_id,
            role=role,
            content=content,
            edited_at=created_at,
            created_at=created_at,
        )
