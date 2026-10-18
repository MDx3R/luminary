from abc import ABC, abstractmethod

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.domain.entity.source import SourceId


class IChatRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: ChatId) -> Chat: ...

    @abstractmethod
    async def get_by_id_for_update(self, id: ChatId) -> Chat | None:
        """Lock current state, including deleted chats, within the caller's UoW."""
        ...

    @abstractmethod
    async def add(self, entity: Chat) -> None: ...

    @abstractmethod
    async def save(self, entity: Chat) -> None: ...

    @abstractmethod
    async def delete_by_folder(self, folder_id: FolderId) -> None: ...

    @abstractmethod
    async def clear_assistant_reference(self, assistant_id: AssistantId) -> None: ...

    @abstractmethod
    async def clear_source_reference(self, source_id: SourceId) -> None: ...

    @abstractmethod
    async def clear_source_association(
        self, chat_id: ChatId, source_id: SourceId
    ) -> None: ...
