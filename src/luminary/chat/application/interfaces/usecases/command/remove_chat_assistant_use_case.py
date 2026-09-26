from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RemoveChatAssistantCommand:
    user_id: UUID
    chat_id: UUID


class IRemoveChatAssistantUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RemoveChatAssistantCommand) -> None: ...
