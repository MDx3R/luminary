from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateChatCommand:
    user_id: UUID
    assistant_id: UUID | None


class ICreateChatUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateChatCommand) -> UUID: ...
