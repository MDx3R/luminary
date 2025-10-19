from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from luminary.chat.domain.enums import Author, MessageStatus


@dataclass(frozen=True)
class GetMessageResponseCommand:
    user_id: UUID
    chat_id: UUID
    message_id: UUID


class StreamState(int, Enum):
    START = "start"
    DELTA = "delta"
    END = "end"


@dataclass(frozen=True)
class StreamingMessageDTO:
    state: StreamState
    content: str
    message_id: UUID
    author: Author
    status: MessageStatus


class IGetStreamingMessageResponseUseCase(ABC):
    @abstractmethod
    def execute(
        self, command: GetMessageResponseCommand
    ) -> AsyncGenerator[StreamingMessageDTO, None]: ...
