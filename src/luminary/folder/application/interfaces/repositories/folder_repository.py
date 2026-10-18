from abc import ABC, abstractmethod

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.source.domain.entity.source import SourceId


class IFolderRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: FolderId) -> Folder: ...

    @abstractmethod
    async def is_deleted_for_update(self, id: FolderId) -> bool:
        """Lock the folder until the caller's transaction ends; missing is false."""
        ...

    @abstractmethod
    async def add(self, entity: Folder) -> None: ...

    @abstractmethod
    async def save(self, entity: Folder) -> None: ...

    @abstractmethod
    async def move_chat_association(
        self, chat_id: ChatId, folder_id: FolderId | None
    ) -> None: ...

    @abstractmethod
    async def clear_assistant_reference(self, assistant_id: AssistantId) -> None: ...

    @abstractmethod
    async def clear_source_reference(self, source_id: SourceId) -> None: ...

    @abstractmethod
    async def clear_chat_association(
        self, folder_id: FolderId, chat_id: ChatId
    ) -> None: ...

    @abstractmethod
    async def clear_source_association(
        self, folder_id: FolderId, source_id: SourceId
    ) -> None: ...
