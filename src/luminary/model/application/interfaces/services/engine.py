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


class IInferenceEngine(ABC):
    @abstractmethod
    def send(
        self, request: InferenceRequestDTO
    ) -> AsyncGenerator[EngineStreamingResponse, None]: ...
