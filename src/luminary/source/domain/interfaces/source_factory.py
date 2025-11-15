from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import overload
from uuid import UUID

from common.domain.value_objects.id import UserId

from luminary.source.domain.entity.source import Source


@dataclass(frozen=True)
class FileSourceFactoryDTO:
    owner_id: UserId
    title: str
    file_id: UUID


@dataclass(frozen=True)
class LinkSourceFactoryDTO:
    owner_id: UserId
    title: str
    url: str


@dataclass(frozen=True)
class PageSourceFactoryDTO:
    owner_id: UserId
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
