from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RemoveSourceFromChatCommand:
    user_id: UUID
    chat_id: UUID
    source_id: UUID


class IRemoveSourceFromChatUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RemoveSourceFromChatCommand) -> None: ...
