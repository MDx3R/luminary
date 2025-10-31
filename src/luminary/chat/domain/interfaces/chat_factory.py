from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from luminary.chat.domain.entity.chat import Chat, ChatSettings


@dataclass(frozen=True)
class ChatFactoryDTO:
    user_id: UUID
    folder_id: UUID | None
    name: str | None
    settings: ChatSettings


class IChatFactory(ABC):
    @abstractmethod
    def create(self, data: ChatFactoryDTO) -> Chat: ...
