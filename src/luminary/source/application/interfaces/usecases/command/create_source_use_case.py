from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO
from uuid import UUID


@dataclass(frozen=True)
class CreateFileSourceCommand:
    user_id: UUID
    title: str
    file_id: UUID


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
    data: BinaryIO


class ICreatePageSourceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreatePageSourceCommand) -> UUID: ...
