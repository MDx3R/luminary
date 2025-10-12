from abc import ABC, abstractmethod
from uuid import UUID

from luminary.file.domain.entity.file import File


class IFileRepository(ABC):
    @abstractmethod
    async def get_by_id(self, file_id: UUID) -> File: ...
    @abstractmethod
    async def add(self, entity: File) -> None: ...
    @abstractmethod
    async def save(self, entity: File) -> None: ...
