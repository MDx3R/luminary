from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ProcessSourceCommand:
    user_id: UUID
    source_id: UUID


class IProcessSourceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: ProcessSourceCommand) -> None: ...
