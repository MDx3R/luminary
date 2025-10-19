from abc import ABC, abstractmethod
from uuid import UUID

from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.enums import Author


class IMessageFactory(ABC):
    @abstractmethod
    def create(
        self, chat_id: UUID, model_id: UUID, role: Author, content: str
    ) -> Message: ...
