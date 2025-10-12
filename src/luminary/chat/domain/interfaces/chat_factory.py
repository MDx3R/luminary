from abc import ABC, abstractmethod
from uuid import UUID

from luminary.chat.domain.entity.chat import Chat


class IChatFactory(ABC):
    @abstractmethod
    def create(self, environment_id: UUID) -> Chat: ...
