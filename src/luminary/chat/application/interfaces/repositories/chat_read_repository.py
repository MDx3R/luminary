from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from luminary.chat.application.interfaces.usecases.query.get_chat_use_case import (
    ChatDTO,
)
from luminary.chat.application.interfaces.usecases.query.get_user_chats_use_case import (
    ChatListItemDTO,
)


class IChatReadRepository(ABC):
    @abstractmethod
    async def get_by_id(self, chat_id: UUID) -> ChatDTO | None: ...
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Sequence[ChatListItemDTO]: ...
    @abstractmethod
    async def get_by_folder_id(self, folder_id: UUID) -> Sequence[ChatListItemDTO]: ...
    @abstractmethod
    async def exists(self, chat_id: UUID) -> bool: ...
