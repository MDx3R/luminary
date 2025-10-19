from abc import ABC, abstractmethod
from uuid import UUID

from luminary.assistant.domain.entity.assisnant import Assistant


class IAssistantRepository(ABC):
    @abstractmethod
    async def get_by_id(self, assistant_id: UUID) -> Assistant: ...
    @abstractmethod
    async def exists_by_name_for_user(self, name: str, user_id: UUID) -> bool: ...
    @abstractmethod
    async def add(self, entity: Assistant) -> None: ...
    @abstractmethod
    async def save(self, entity: Assistant) -> None: ...
    @abstractmethod
    async def remove(self, entity: Assistant) -> None: ...
