from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ProviderStreamingResponse:
    content: str
    response_tokens: int


@dataclass(frozen=True)
class ProviderResponse:
    content: str
    response_tokens: int


class AIProvider(ABC):
    @abstractmethod
    async def completion(
        self, messages: list[str], system_prompt: str
    ) -> ProviderResponse: ...

    @abstractmethod
    def stream_completion(
        self, messages: list[str], model_id: UUID
    ) -> AsyncGenerator[ProviderStreamingResponse, None]: ...
