from abc import ABC, abstractmethod

from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assisnant import Assistant


class IAssistantFactory(ABC):
    @abstractmethod
    def create(
        self, user_id: UserId, name: str, description: str, prompt: str | None
    ) -> Assistant: ...
