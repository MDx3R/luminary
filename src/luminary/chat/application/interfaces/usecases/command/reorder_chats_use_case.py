from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ReorderChatsCommand:
    user_id: UUID
    folder_id: UUID | None
    chat_ids: list[UUID]


class IReorderChatsUseCase(ABC):
    @abstractmethod
    async def execute(self, command: ReorderChatsCommand) -> None: ...
