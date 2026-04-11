from abc import ABC, abstractmethod

from luminary.assistant.domain.entity.assistant import Assistant, AssistantId


class IAssistantRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: AssistantId) -> Assistant: ...
    @abstractmethod
    async def add(self, entity: Assistant) -> None: ...
    @abstractmethod
    async def save(self, entity: Assistant) -> None: ...
