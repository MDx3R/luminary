from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from uuid import UUID

from luminary.chat.domain.entity.chat import Chat


class IChatRepository(ABC):
    @abstractmethod
    async def get_by_id(self, chat_id: UUID) -> Chat: ...
    @abstractmethod
    async def get_by_folder_id(self, folder_id: UUID) -> Sequence[Chat]: ...
    @abstractmethod
    async def add(self, entity: Chat) -> None: ...
    @abstractmethod
    async def save(self, entity: Chat) -> None: ...
    @abstractmethod
    async def save_all(self, entities: Iterable[Chat]) -> None: ...
