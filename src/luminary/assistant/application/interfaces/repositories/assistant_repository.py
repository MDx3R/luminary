from abc import ABC, abstractmethod

from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assisnant import Assistant, AssistantId


class IAssistantRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: AssistantId) -> Assistant: ...
    @abstractmethod
    async def exists_by_name_for_user(self, name: str, user_id: UserId) -> bool: ...
    @abstractmethod
    async def add(self, entity: Assistant) -> None: ...
    @abstractmethod
    async def save(self, entity: Assistant) -> None: ...
    @abstractmethod
    async def remove(self, entity: Assistant) -> None: ...
