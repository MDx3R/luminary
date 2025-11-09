from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from luminary.source.domain.value_objects.file_meta import FileMeta


@dataclass(frozen=True)
class CreateFileSourceCommand:
    user_id: UUID
    title: str
    meta: FileMeta


class ICreateFileSourceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateFileSourceCommand) -> UUID: ...


@dataclass(frozen=True)
class CreateLinkSourceCommand:
    user_id: UUID
    title: str
    url: str


class ICreateLinkSourceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateLinkSourceCommand) -> UUID: ...


@dataclass(frozen=True)
class CreatePageSourceCommand:
    user_id: UUID
    title: str


class ICreatePageSourceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreatePageSourceCommand) -> UUID: ...
