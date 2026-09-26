from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator, Sequence
from dataclasses import dataclass
from enum import Enum
from uuid import UUID


@dataclass(frozen=True)
class EngineStreamingResponse:
    content: str


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class InferenceMode(str, Enum):
    CHAT = "chat"
    EDITOR_INLINE = "editor_inline"
    EDITOR_AUTOCOMPLETE = "editor_autocomplete"


class ChatSourceContext(str, Enum):
    """Where chat-attached sources come from (folder vs standalone)."""

    FOLDER = "folder"
    STANDALONE = "standalone"


@dataclass(frozen=True)
class MessageDTO:
    content: str
    role: Role


@dataclass(frozen=True)
class InferenceRequestDTO:
    query: str
    system_prompt: str
    source_ids: Sequence[UUID]
    history: Sequence[MessageDTO]
    editor_content: str | None = None
    mode: InferenceMode = InferenceMode.CHAT
    chat_source_context: ChatSourceContext | None = None


class IInferenceEngine(ABC):
    @abstractmethod
    def send(
        self, request: InferenceRequestDTO
    ) -> AsyncGenerator[EngineStreamingResponse, None]: ...
