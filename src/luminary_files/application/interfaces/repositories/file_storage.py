from abc import ABC, abstractmethod
from collections.abc import Iterable, Sequence
from datetime import timedelta
from typing import BinaryIO

from common.domain.value_objects.object_key import ObjectKey


class IFileStorage(ABC):
    @abstractmethod
    async def get(self, object_key: ObjectKey) -> BinaryIO: ...
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
        self, object_keys: Iterable[ObjectKey], expires_in: timedelta
    ) -> Sequence[str]: ...
