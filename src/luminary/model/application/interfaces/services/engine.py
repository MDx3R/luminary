from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from uuid import UUID

from luminary.chat.application.interfaces.usecases.command.send_message_use_case import (
    MessageDTO,
)


@dataclass(frozen=True)
class EngineStreamingResponse:
    content: str
    response_tokens: int = 0


class IEngine(ABC):
    @abstractmethod
    def send(
        self,
        query: str,
        *,
        system_prompt: str,
        source_ids: list[UUID],
        history: list[MessageDTO],
    ) -> AsyncGenerator[EngineStreamingResponse, None]: ...
