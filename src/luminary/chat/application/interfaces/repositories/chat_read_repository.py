"""Read repository interface for Chat query side."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from luminary.chat.application.dtos.read_models import (
    ChatReadModel,
    ChatSummaryReadModel,
    MessageReadModel,
)


class IChatReadRepository(ABC):
    """Returns read models for chat queries; access controlled via owner_id."""

    @abstractmethod
    async def get_by_id(self, chat_id: UUID, owner_id: UUID) -> ChatReadModel:
        """Return chat read model or raise NotFoundError if not found or not owned."""
        ...

    @abstractmethod
    async def list_standalone_by_owner(
        self, owner_id: UUID
    ) -> Sequence[ChatSummaryReadModel]:
        """Return standalone chats (folder_id IS NULL) for the owner."""
        ...

    @abstractmethod
    async def list_messages(
        self,
        chat_id: UUID,
        owner_id: UUID,
        *,
        limit: int = 50,
        before: UUID | None = None,
    ) -> Sequence[MessageReadModel]:
        """Return messages for the chat (cursor-based), access checked by owner_id."""
        ...
