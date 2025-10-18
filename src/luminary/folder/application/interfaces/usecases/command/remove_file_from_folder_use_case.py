from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RemoveFileFromFolderCommand:
    user_id: UUID
    folder_id: UUID
    file_id: UUID


class IRemoveFileFromFolderUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RemoveFileFromFolderCommand) -> None: ...
