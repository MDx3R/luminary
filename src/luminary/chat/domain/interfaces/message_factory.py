from abc import ABC, abstractmethod
from dataclasses import dataclass

from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.enums import Author
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.model.domain.entity.model import ModelId


@dataclass(frozen=True)
class MessageFactoryDTO:
    chat_id: ChatId
    model_id: ModelId
    role: Author
    content: str


class IMessageFactory(ABC):
    @abstractmethod
    def create(self, data: MessageFactoryDTO) -> Message: ...
