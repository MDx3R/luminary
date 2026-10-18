from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ReorderFoldersCommand:
    user_id: UUID
    folder_id: UUID
    previous_folder_id: UUID | None = None
    next_folder_id: UUID | None = None


class IReorderFoldersUseCase(ABC):
    @abstractmethod
    async def execute(self, command: ReorderFoldersCommand) -> None: ...
