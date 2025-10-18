from abc import ABC, abstractmethod
from uuid import UUID

from luminary.folder.domain.entity.folder import Folder


class IFolderRepository(ABC):
    @abstractmethod
    async def get_by_id(self, folder_id: UUID) -> Folder: ...
    @abstractmethod
    async def add(self, entity: Folder) -> None: ...
    @abstractmethod
    async def save(self, entity: Folder) -> None: ...
