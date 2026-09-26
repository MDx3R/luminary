from abc import ABC, abstractmethod

from common.domain.value_objects.id import UserId
from luminary_files.domain.entity.file import File


class IFileFactory(ABC):
    @abstractmethod
    def create(
        self, user_id: UserId, filename: str, bucket: str, mime: str
    ) -> File: ...
