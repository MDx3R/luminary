from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RemoveSourceFromFolderCommand:
    user_id: UUID
    folder_id: UUID
    source_id: UUID


class IRemoveSourceFromFolderUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RemoveSourceFromFolderCommand) -> None: ...
