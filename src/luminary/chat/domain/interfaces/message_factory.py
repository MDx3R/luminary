from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.enums import Author


@dataclass(frozen=True)
class MessageFactoryDTO:
    chat_id: UUID
    model_id: UUID
    role: Author
    content: str


class IMessageFactory(ABC):
    @abstractmethod
    def create(self, data: MessageFactoryDTO) -> Message: ...
