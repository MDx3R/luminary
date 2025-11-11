from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class GetUserChatsQuery:
    user_id: UUID
    folder_id: UUID | None = None


@dataclass(frozen=True)
class ChatListItemDTO:
    chat_id: UUID
    name: str
    created_at: datetime
    updated_at: datetime


class IGetUserChatsUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetUserChatsQuery) -> Sequence[ChatListItemDTO]: ...
