from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from enum import Enum
from typing import Final
from uuid import UUID

from luminary.chat.domain.enums import Author, MessageStatus


EMPTY_CONTENT: Final[str] = ""
STREAM_START_CONTENT: Final[str] = "start"
STREAM_END_CONTENT: Final[str] = "end"


@dataclass(frozen=True)
class GetMessageResponseCommand:
    user_id: UUID
    chat_id: UUID
    message_id: UUID


class StreamState(str, Enum):
    START = "start"
    DELTA = "delta"
    END = "end"
    ERROR = "error"


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
