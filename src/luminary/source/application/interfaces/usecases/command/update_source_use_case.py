from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateSourceCommand:
    user_id: UUID
    source_id: UUID
    title: str


class IUpdateSourceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: UpdateSourceCommand) -> None: ...
