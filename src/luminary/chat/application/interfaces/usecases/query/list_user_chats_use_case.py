"""Query use case: list standalone chats for a user."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from luminary.chat.application.dtos.read_models import ChatSummaryReadModel


@dataclass(frozen=True)
class ListUserChatsQuery:
    user_id: UUID


class IListUserChatsUseCase(ABC):
    @abstractmethod
    async def execute(
        self, query: ListUserChatsQuery
    ) -> Sequence[ChatSummaryReadModel]:
        """Return standalone chats owned by the user."""
        ...
