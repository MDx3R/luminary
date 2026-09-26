"""Query use case: get chat by id."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from luminary.chat.application.dtos.read_models import ChatReadModel


@dataclass(frozen=True)
class GetChatByIdQuery:
    user_id: UUID
    chat_id: UUID


class IGetChatByIdUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetChatByIdQuery) -> ChatReadModel:
        """Return chat read model for the given id and owner."""
        ...
