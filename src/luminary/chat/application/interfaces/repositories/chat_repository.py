from abc import ABC, abstractmethod
from collections.abc import Sequence

from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.domain.entity.source import SourceId


class IChatRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: ChatId) -> Chat: ...

    @abstractmethod
    async def add(self, entity: Chat) -> None: ...

    @abstractmethod
    async def save(self, entity: Chat) -> None: ...

    @abstractmethod
    async def list_ids_by_location(
        self, owner_id: UserId, folder_id: FolderId | None
    ) -> Sequence[ChatId]: ...

    @abstractmethod
    async def set_order(
        self, owner_id: UserId, folder_id: FolderId | None, chat_ids: Sequence[ChatId]
    ) -> None: ...

    @abstractmethod
    async def move_to_folder(
        self, chat_id: ChatId, folder_id: FolderId | None
    ) -> None: ...

    @abstractmethod
    async def clear_assistant_reference(self, assistant_id: AssistantId) -> None: ...

    @abstractmethod
    async def clear_source_reference(self, source_id: SourceId) -> None: ...

    @abstractmethod
    async def clear_source_association(
        self, chat_id: ChatId, source_id: SourceId
    ) -> None: ...
