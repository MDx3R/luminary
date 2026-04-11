from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO
from uuid import UUID


@dataclass(frozen=True)
class GetContentQuery:
    user_id: UUID
    content_id: UUID


@dataclass(frozen=True)
class ProcessFileCommand:
    user_id: UUID
    data: BinaryIO
    filename: str


@dataclass(frozen=True)
class ProcessLinkCommand:
    user_id: UUID
    url: str


class IContentService(ABC):
    @abstractmethod
    async def get_content(self, query: GetContentQuery) -> BinaryIO: ...
    @abstractmethod
    async def process_file(self, command: ProcessFileCommand) -> UUID: ...
    @abstractmethod
    async def process_link(self, command: ProcessLinkCommand) -> UUID: ...
