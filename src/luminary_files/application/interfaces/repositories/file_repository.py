from abc import ABC, abstractmethod

from common.domain.value_objects.object_key import ObjectKey
from luminary_files.domain.entity.file import File, FileId


class IFileRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: FileId) -> File: ...
    @abstractmethod
    async def get_by_object_key(self, key: ObjectKey) -> File: ...
    @abstractmethod
    async def add(self, entity: File) -> None: ...
