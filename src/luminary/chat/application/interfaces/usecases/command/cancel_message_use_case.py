from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CancelMessageCommand:
    user_id: UUID
    chat_id: UUID
    message_id: UUID


class ICancelMessageUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CancelMessageCommand) -> None: ...
