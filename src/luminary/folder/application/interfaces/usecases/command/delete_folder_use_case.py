from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeleteFolderCommand:
    user_id: UUID
    folder_id: UUID


class IDeleteFolderUseCase(ABC):
    @abstractmethod
    async def execute(self, command: DeleteFolderCommand) -> None: ...
