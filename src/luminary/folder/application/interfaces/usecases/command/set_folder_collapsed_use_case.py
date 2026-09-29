from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SetFolderCollapsedCommand:
    user_id: UUID
    folder_id: UUID
    collapsed: bool


class ISetFolderCollapsedUseCase(ABC):
    @abstractmethod
    async def execute(self, command: SetFolderCollapsedCommand) -> None: ...
