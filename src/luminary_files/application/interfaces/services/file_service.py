from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO
from uuid import UUID


@dataclass(frozen=True)
class UploadFileCommand:
    user_id: UUID
    filename: str
    content: BinaryIO


@dataclass(frozen=True)
class GetFileQuery:
    user_id: UUID
    file_id: UUID


class IFileService(ABC):
    @abstractmethod
    async def get_file(self, query: GetFileQuery) -> BinaryIO: ...
    @abstractmethod
    async def upload_file(self, command: UploadFileCommand) -> UUID: ...
