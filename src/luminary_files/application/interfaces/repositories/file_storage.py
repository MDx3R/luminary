from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import timedelta
from typing import BinaryIO

from luminary_files.domain.entity.file import ObjectKey


class IFileStorage(ABC):
    @abstractmethod
    async def upload(
        self, object_key: ObjectKey, mime: str, data: BinaryIO
    ) -> None: ...
    @abstractmethod
    async def get_presigned_get_url(
        self, object_key: ObjectKey, expires_in: timedelta
    ) -> str: ...
    @abstractmethod
    async def get_presigned_get_urls(
        self, object_keys: Sequence[ObjectKey], expires_in: timedelta
    ) -> list[str]: ...
