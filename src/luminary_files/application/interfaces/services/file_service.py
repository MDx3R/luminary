from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO
from uuid import UUID

from luminary_files.application.dtos.query.get_presigned_url_query import (
    GetPresignedUrlQuery,
)


@dataclass(frozen=True)
class UploadFileCommand:
    user_id: UUID
    filename: str
    content: BinaryIO


@dataclass(frozen=True)
class GetFileQuery:
    user_id: UUID
    object_key: str


class IFileService(ABC):
    @abstractmethod
    async def get_file(self, query: GetFileQuery) -> BinaryIO: ...
    @abstractmethod
    async def upload_file(self, command: UploadFileCommand) -> UUID: ...
    @abstractmethod
    async def get_file_presigned_url(self, query: GetPresignedUrlQuery) -> str: ...
