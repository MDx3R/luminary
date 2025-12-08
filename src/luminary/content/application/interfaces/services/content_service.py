from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO
from uuid import UUID


# TODO: Use file object key instead of data
@dataclass(frozen=True)
class ProcessFileCommand:
    user_id: UUID
    data: BinaryIO
    # file_id: UUID


@dataclass(frozen=True)
class ProcessLinkCommand:
    user_id: UUID
    url: str


@dataclass(frozen=True)
class GetContentPresignedUrlQuery:
    object_key: str


class IContentService(ABC):
    @abstractmethod
    async def process_file(self, command: ProcessFileCommand) -> UUID: ...
    @abstractmethod
    async def process_link(self, command: ProcessLinkCommand) -> UUID: ...
