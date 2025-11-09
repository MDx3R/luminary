from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Self
from uuid import UUID

from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime

from luminary.chat.domain.entity.attachment import Attachment
from luminary.chat.domain.enums import Author, MessageStatus


@dataclass
class Message:
    message_id: UUID
    chat_id: UUID
    role: Author
    status: MessageStatus
    content: str
    model_id: UUID
    edited_at: DateTime
    created_at: DateTime
    tokens: int | None = None
    _attachments: set[Attachment] = field(default_factory=set[Attachment])

    def __post_init__(self) -> None:
        if self.tokens and self.tokens < 0:
            raise InvariantViolationError("Tokens cannot be negative")

    @property
    def attachments(self) -> Sequence[Attachment]:
        return list(self._attachments)

    def add_chunk(self, chunk: str) -> None:
        self.content += chunk

    def add_attachment(self, attachemt: Attachment) -> None:
        if self.role != Author.USER:
            raise InvariantViolationError(
                "Attachemnt cannot be added for non-user message"
            )
        self._attachments.add(attachemt)

    def start_processing(self) -> None:
        self.status = MessageStatus.PROCESSING

    def start_streaming(self) -> None:
        self.status = MessageStatus.STREAMING

    def cancel(self) -> None:
        self.status = MessageStatus.CANCELLED

    def fail(self) -> None:
        self.status = MessageStatus.FAILED

    def complete(self, tokens: int) -> None:
        self.tokens = tokens
        self.status = MessageStatus.COMPLETED

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        message_id: UUID,
        chat_id: UUID,
        role: Author,
        status: MessageStatus,
        content: str,
        model_id: UUID,
        created_at: DateTime,
    ) -> Self:
        return cls(
            message_id=message_id,
            chat_id=chat_id,
            model_id=model_id,
            role=role,
            status=status,
            content=content,
            edited_at=created_at,
            created_at=created_at,
        )
