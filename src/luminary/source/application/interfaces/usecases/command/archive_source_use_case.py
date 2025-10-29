from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ArchiveSourceCommand:
    user_id: UUID
    source_id: UUID


class IArchiveSourceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: ArchiveSourceCommand) -> None: ...
