from abc import ABC, abstractmethod
from uuid import UUID

from luminary.chat.domain.entity.message import ChatMessage
from luminary.chat.domain.enums import ChatMessageAuthor


class IMessageFactory(ABC):
    @abstractmethod
    def create(
        self, chat_id: UUID, role: ChatMessageAuthor, content: str
    ) -> ChatMessage: ...
