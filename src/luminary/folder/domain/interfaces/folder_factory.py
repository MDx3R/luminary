from abc import ABC, abstractmethod

from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assisnant import AssistantId
from luminary.folder.domain.entity.folder import Folder
from luminary.model.domain.entity.model import ModelId


class IFolderFactory(ABC):
    @abstractmethod
    def create(
        self,
        name: str,
        description: str | None,
        user_id: UserId,
        model_id: ModelId,
        assistant_id: AssistantId,
    ) -> Folder: ...
