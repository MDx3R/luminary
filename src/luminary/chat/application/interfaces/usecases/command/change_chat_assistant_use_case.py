from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ChangeChatAssistantCommand:
    user_id: UUID
    chat_id: UUID
    assistant_id: UUID


class IChangeChatAssistantUseCase(ABC):
    @abstractmethod
    async def execute(self, command: ChangeChatAssistantCommand) -> None: ...
