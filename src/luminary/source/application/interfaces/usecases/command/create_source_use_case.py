from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from common.domain.value_objects.datetime import DateTime


@dataclass(frozen=True)
class CreateSourceCommand:
    user_id: UUID
    name: str


@dataclass(frozen=True)
class SourceDTO:
    source_id: UUID
    user_id: UUID
    name: str
    created_at: DateTime


class ICreateSourceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateSourceCommand) -> SourceDTO: ...
