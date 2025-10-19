from abc import ABC, abstractmethod
from uuid import UUID

from luminary.assistant.domain.entity.assisnant import Assistant


class IAssistantAccessPolicy(ABC):
    @abstractmethod
    def is_allowed(self, user_id: UUID, assistant: Assistant) -> bool: ...

    @abstractmethod
    def assert_is_allowed(self, user_id: UUID, assistant: Assistant) -> None: ...
