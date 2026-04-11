from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateChatSettingsCommand:
    user_id: UUID
    chat_id: UUID
    model_id: UUID
    max_context_messages: int


class IUpdateChatSettingsUseCase(ABC):
    @abstractmethod
    async def execute(self, command: UpdateChatSettingsCommand) -> None: ...
