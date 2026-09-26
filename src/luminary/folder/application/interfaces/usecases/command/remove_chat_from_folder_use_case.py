from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RemoveChatFromFolderCommand:
    user_id: UUID
    folder_id: UUID
    chat_id: UUID


class IRemoveChatFromFolderUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RemoveChatFromFolderCommand) -> None: ...
