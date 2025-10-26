from abc import ABC, abstractmethod
from uuid import UUID

from luminary.assistant.domain.entity.assisnant import Assistant


class IAssistantFactory(ABC):
    @abstractmethod
    def create(
        self, user_id: UUID, name: str, description: str, prompt: str | None
    ) -> Assistant: ...
