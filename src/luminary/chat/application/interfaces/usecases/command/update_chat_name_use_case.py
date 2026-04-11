from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateChatNameCommand:
    user_id: UUID
    chat_id: UUID
    name: str


class IUpdateChatNameUseCase(ABC):
    @abstractmethod
    async def execute(self, command: UpdateChatNameCommand) -> None: ...
