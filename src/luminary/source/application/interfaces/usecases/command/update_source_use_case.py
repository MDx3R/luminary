from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from luminary.source.application.interfaces.usecases.command.create_source_use_case import (
    SourceDTO,
)


@dataclass(frozen=True)
class UpdateSourceCommand:
    user_id: UUID
    source_id: UUID
    name: str


class IUpdateSourceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: UpdateSourceCommand) -> SourceDTO: ...
