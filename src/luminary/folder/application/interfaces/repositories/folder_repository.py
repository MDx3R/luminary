from abc import ABC, abstractmethod

from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.domain.entity.source import SourceId


class IFolderRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: FolderId) -> Folder: ...
    @abstractmethod
    async def add(self, entity: Folder) -> None: ...
    @abstractmethod
    async def save(self, entity: Folder) -> None: ...
    @abstractmethod
    async def remove_chat(self, folder_id: FolderId, chat_id: ChatId) -> None: ...
    @abstractmethod
    async def remove_source(self, folder_id: FolderId, source_id: SourceId) -> None: ...
