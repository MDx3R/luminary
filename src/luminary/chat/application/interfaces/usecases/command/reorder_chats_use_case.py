from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ReorderChatsCommand:
    user_id: UUID
    chat_id: UUID
    previous_chat_id: UUID | None = None
    next_chat_id: UUID | None = None


class IReorderChatsUseCase(ABC):
    @abstractmethod
    async def execute(self, command: ReorderChatsCommand) -> None: ...
