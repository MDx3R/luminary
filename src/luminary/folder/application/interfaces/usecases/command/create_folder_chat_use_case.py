from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateFolderChatCommand:
    user_id: UUID
    folder_id: UUID
    name: str | None
    assistant_id: UUID | None
    model_id: UUID
    max_context_messages: int


class ICreateFolderChatUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateFolderChatCommand) -> UUID: ...
