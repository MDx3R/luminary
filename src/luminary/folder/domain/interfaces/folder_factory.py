from abc import ABC, abstractmethod

from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.folder.domain.entity.folder import Folder


class IFolderFactory(ABC):
    @abstractmethod
    def create(
        self,
        name: str,
        description: str | None,
        user_id: UserId,
        assistant_id: AssistantId | None,
    ) -> Folder: ...
