from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import overload
from uuid import UUID

from luminary.source.domain.entity.source import Source
from luminary.source.domain.value_objects.file_meta import FileMeta


@dataclass(frozen=True)
class FileSourceFactoryDTO:
    owner_id: UUID
    title: str
    meta: FileMeta


@dataclass(frozen=True)
class LinkSourceFactoryDTO:
    owner_id: UUID
    title: str
    url: str


@dataclass(frozen=True)
class PageSourceFactoryDTO:
    owner_id: UUID
    title: str


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
