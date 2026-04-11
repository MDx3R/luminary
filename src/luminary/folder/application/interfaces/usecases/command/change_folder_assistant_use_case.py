from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ChangeFolderAssistantCommand:
    user_id: UUID
    folder_id: UUID
    assistant_id: UUID


class IChangeFolderAssistantUseCase(ABC):
    @abstractmethod
    async def execute(self, command: ChangeFolderAssistantCommand) -> None: ...
