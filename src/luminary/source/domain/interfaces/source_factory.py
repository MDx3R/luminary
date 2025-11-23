from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import overload

from common.domain.value_objects.id import UserId
from luminary_files.domain.entity.file import FileId

from luminary.content.domain.entity.content import ContentId
from luminary.source.domain.entity.source import Source


@dataclass(frozen=True)
class FileSourceFactoryDTO:
    owner_id: UserId
    title: str
    file_id: FileId


@dataclass(frozen=True)
class LinkSourceFactoryDTO:
    owner_id: UserId
    title: str
    url: str


@dataclass(frozen=True)
class PageSourceFactoryDTO:
    owner_id: UserId
    title: str
    content_id: ContentId


class ISourceFactory(ABC):
    @overload
    def create(self, data: FileSourceFactoryDTO) -> Source: ...
    @overload
    def create(self, data: LinkSourceFactoryDTO) -> Source: ...
    @overload
    def create(self, data: PageSourceFactoryDTO) -> Source: ...
    @abstractmethod
    def create(
        self, data: FileSourceFactoryDTO | LinkSourceFactoryDTO | PageSourceFactoryDTO
    ) -> Source: ...
