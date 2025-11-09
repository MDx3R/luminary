from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import overload
from uuid import UUID

from common.domain.value_objects.datetime import DateTime

from luminary.source.domain.entity.source import Source
from luminary.source.domain.value_objects.file_meta import FileMeta


@dataclass(frozen=True)
class FileSourceFactoryDTO:
    source_id: UUID
    owner_id: UUID
    title: str
    created_at: DateTime
    meta: FileMeta


@dataclass(frozen=True)
class LinkSourceFactoryDTO:
    source_id: UUID
    owner_id: UUID
    title: str
    created_at: DateTime
    url: str


@dataclass(frozen=True)
class PageSourceFactoryDTO:
    source_id: UUID
    owner_id: UUID
    title: str
    created_at: DateTime


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
