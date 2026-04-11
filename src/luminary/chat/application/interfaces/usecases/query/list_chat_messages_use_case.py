"""Query use case: list messages in a chat (cursor-based)."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from luminary.chat.application.dtos.read_models import MessageReadModel


@dataclass(frozen=True)
class ListChatMessagesQuery:
    user_id: UUID
    chat_id: UUID
    limit: int = 50
    before: UUID | None = None


class IListChatMessagesUseCase(ABC):
    @abstractmethod
    async def execute(self, query: ListChatMessagesQuery) -> Sequence[MessageReadModel]:
        """Return messages for the chat (cursor-based)."""
        ...
