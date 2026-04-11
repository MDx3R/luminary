from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SendMessageCommand:
    user_id: UUID
    chat_id: UUID
    content: str


class ISendMessageUseCase(ABC):
    @abstractmethod
    async def execute(self, command: SendMessageCommand) -> UUID: ...
