from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RemoveFolderAssistantCommand:
    user_id: UUID
    folder_id: UUID


class IRemoveFolderAssistantUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RemoveFolderAssistantCommand) -> None: ...
