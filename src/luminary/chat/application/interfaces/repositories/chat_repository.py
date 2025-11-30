from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence

from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.domain.value_objects.folder_id import FolderId


class IChatRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: ChatId) -> Chat: ...
    @abstractmethod
    async def get_by_folder_id(self, folder_id: FolderId) -> Sequence[Chat]: ...
    @abstractmethod
    async def add(self, entity: Chat) -> None: ...
    @abstractmethod
    async def save(self, entity: Chat) -> None: ...
    @abstractmethod
    async def save_all(self, entities: Iterable[Chat]) -> None: ...
