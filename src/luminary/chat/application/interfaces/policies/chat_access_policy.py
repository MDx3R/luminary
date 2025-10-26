from abc import ABC, abstractmethod
from uuid import UUID

from luminary.chat.domain.entity.chat import Chat


class IChatAccessPolicy(ABC):
    @abstractmethod
    def is_allowed(self, user_id: UUID, chat: Chat) -> bool: ...

    @abstractmethod
    def assert_is_allowed(self, user_id: UUID, chat: Chat) -> None: ...
