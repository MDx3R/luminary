from abc import ABC, abstractmethod
from uuid import UUID

from luminary.chat.domain.entity.chat import Chat


class IChatRepository(ABC):
    @abstractmethod
    async def get_by_id(self, chat_id: UUID) -> Chat: ...
    @abstractmethod
    async def get_by_environment_id(self, environment_id: UUID) -> Chat: ...
    @abstractmethod
    async def add(self, entity: Chat) -> None: ...
    @abstractmethod
    async def save(self, entity: Chat) -> None: ...
