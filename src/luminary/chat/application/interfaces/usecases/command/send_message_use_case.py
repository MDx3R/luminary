from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from common.domain.value_objects.datetime import DateTime

from luminary.chat.domain.enums import Author, MessageStatus


@dataclass(frozen=True)
class SendMessageCommand:
    user_id: UUID
    chat_id: UUID
    message: str


@dataclass(frozen=True)
class MessageDTO:
    message_id: UUID
    chat_id: UUID
    author: Author
    status: MessageStatus
    content: str
    tokens: int | None
    created_at: DateTime


class ISendMessageUseCase(ABC):
    @abstractmethod
    async def execute(self, command: SendMessageCommand) -> MessageDTO: ...
