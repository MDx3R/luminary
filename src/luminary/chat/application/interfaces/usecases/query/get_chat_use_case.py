from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class GetChatQuery:
    user_id: UUID
    chat_id: UUID


@dataclass(frozen=True)
class ChatDTO:
    chat_id: UUID
    user_id: UUID
    folder_id: UUID | None
    name: str
    model_id: UUID
    system_prompt: str
    max_context_messages: int
    created_at: datetime
    updated_at: datetime


class IGetChatUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetChatQuery) -> ChatDTO: ...
