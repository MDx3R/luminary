from abc import ABC, abstractmethod
from uuid import UUID

from luminary.folder.domain.entity.folder import Folder


class IFolderAccessPolicy(ABC):
    @abstractmethod
    def is_allowed(self, user_id: UUID, folder: Folder) -> bool: ...

    @abstractmethod
    def assert_is_allowed(self, user_id: UUID, folder: Folder) -> None: ...
