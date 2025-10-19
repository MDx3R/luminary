from abc import ABC, abstractmethod
from uuid import UUID

from luminary.chat.domain.entity.chat import Chat, ChatSettings


class IChatFactory(ABC):
    @abstractmethod
    def create(
        self,
        user_id: UUID,
        folder_id: UUID | None,
        name: str | None,
        settings: ChatSettings,
    ) -> Chat: ...
