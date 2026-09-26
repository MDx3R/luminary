from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from luminary.model.application.dto.request import (
    OllamaChatRequest,
    OllamaGenerateRequest,
)
from luminary.model.application.dto.response import (
    OllamaChatResponse,
    OllamaGenerateResponse,
    OllamaModelsResponse,
)


class IOllamaService(ABC):
    @abstractmethod
    async def list_models(self) -> OllamaModelsResponse: ...
    @abstractmethod
    def generate(
        self, command: OllamaGenerateRequest
    ) -> AsyncGenerator[OllamaGenerateResponse]: ...
    @abstractmethod
    def chat(
        self, command: OllamaChatRequest
    ) -> AsyncGenerator[OllamaChatResponse]: ...
