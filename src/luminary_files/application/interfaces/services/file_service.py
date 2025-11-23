from abc import ABC, abstractmethod
from typing import BinaryIO
from uuid import UUID

from luminary_files.application.dtos.query.get_presigned_url_query import (
    GetPresignedUrlQuery,
)


class UploadFileCommand:
    user_id: UUID
    filename: str
    content: BinaryIO


class DeleteFileCommand:
    user_id: UUID
    object_key: str


class IFileService(ABC):
    @abstractmethod
    async def upload_file(self, command: UploadFileCommand) -> str: ...
    @abstractmethod
    async def get_file_presigned_url(self, query: GetPresignedUrlQuery) -> str: ...
