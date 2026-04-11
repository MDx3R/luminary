from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateChatCommand:
    user_id: UUID
    folder_id: UUID | None
    name: str | None
    assistant_id: UUID | None
    model_id: UUID
    max_context_messages: int


class ICreateChatUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateChatCommand) -> UUID: ...
