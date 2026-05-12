from abc import ABC, abstractmethod
from dataclasses import dataclass

from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.domain.entity.chat import Chat
from luminary.folder.domain.value_objects.folder_id import FolderId


@dataclass(frozen=True)
class ChatFactoryDTO:
    user_id: UserId
    folder_id: FolderId | None
    name: str | None
    assistant_id: AssistantId | None


class IChatFactory(ABC):
    @abstractmethod
    def create(self, data: ChatFactoryDTO) -> Chat: ...
