from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class MoveChatCommand:
    user_id: UUID
    chat_id: UUID
    folder_id: UUID | None


class IMoveChatUseCase(ABC):
    @abstractmethod
    async def execute(self, command: MoveChatCommand) -> None: ...
