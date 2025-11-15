from abc import ABC, abstractmethod

from luminary.folder.domain.entity.folder import Folder, FolderId


class IFolderRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: FolderId) -> Folder: ...
    @abstractmethod
    async def add(self, entity: Folder) -> None: ...
    @abstractmethod
    async def save(self, entity: Folder) -> None: ...
