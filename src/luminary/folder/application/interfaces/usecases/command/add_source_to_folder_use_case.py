from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AddSourceToFolderCommand:
    user_id: UUID
    folder_id: UUID
    source_id: UUID


class IAddSourceToFolderUseCase(ABC):
    @abstractmethod
    async def execute(self, command: AddSourceToFolderCommand) -> None: ...
