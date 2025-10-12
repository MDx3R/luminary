from abc import ABC, abstractmethod
from uuid import UUID

from luminary.file.domain.entity.file import File


class IFileFactory(ABC):
    @abstractmethod
    def create(
        self, user_id: UUID, filename: str, extension: str, mime: str
    ) -> File: ...
