from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeleteChatCommand:
    user_id: UUID
    chat_id: UUID


class IDeleteChatUseCase(ABC):
    @abstractmethod
    async def execute(self, command: DeleteChatCommand) -> None: ...
