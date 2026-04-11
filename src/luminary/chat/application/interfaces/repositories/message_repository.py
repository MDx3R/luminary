from abc import ABC, abstractmethod

from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.value_objects.message_id import MessageId


class IMessageRepository(ABC):
    """Repository for Message aggregate (for future inference use cases)."""

    @abstractmethod
    async def get_by_id(self, id: MessageId) -> Message: ...

    @abstractmethod
    async def add(self, entity: Message) -> None: ...

    @abstractmethod
    async def save(self, entity: Message) -> None: ...
