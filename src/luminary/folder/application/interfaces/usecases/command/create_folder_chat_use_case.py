from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateFolderChatCommand:
    user_id: UUID
    folder_id: UUID
    # TODO: Add name field


class ICreateFolderChatUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateFolderChatCommand) -> UUID: ...
