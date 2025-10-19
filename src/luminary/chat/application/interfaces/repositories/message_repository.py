from abc import ABC, abstractmethod
from uuid import UUID

from luminary.chat.domain.entity.message import Message


class IMessageRepository(ABC):
    @abstractmethod
    async def get_by_id(self, message_id: UUID) -> Message: ...
    @abstractmethod
    async def add(self, entity: Message) -> None: ...
    @abstractmethod
    async def save(self, entity: Message) -> None: ...
