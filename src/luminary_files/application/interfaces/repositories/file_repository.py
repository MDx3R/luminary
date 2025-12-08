from abc import ABC, abstractmethod

from luminary_files.domain.entity.file import File


class IFileRepository(ABC):
    @abstractmethod
    async def add(self, entity: File) -> None: ...
