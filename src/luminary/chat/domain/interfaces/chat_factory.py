from abc import ABC, abstractmethod
from uuid import UUID

from luminary.chat.domain.entity.chat import Chat


class IChatFactory(ABC):
    @abstractmethod
    def create(self, folder_id: UUID, user_id: UUID, name: str | None) -> Chat: ...
