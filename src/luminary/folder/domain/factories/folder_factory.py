from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator
from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assisnant import AssistantId
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.domain.interfaces.folder_factory import (
    IFolderFactory,
)
from luminary.folder.domain.value_objects.folder_id import FolderId


class FolderFactory(IFolderFactory):
    def __init__(self, clock: IClock, uuid_generator: IUUIDGenerator) -> None:
        self.clock = clock
        self.uuid_generator = uuid_generator

    def create(
        self,
        name: str,
        description: str | None,
        user_id: UserId,
        assistant_id: AssistantId | None,
    ) -> Folder:
        return Folder.create(
            id=FolderId(self.uuid_generator.create()),
            name=name,
            description=description,
            owner_id=user_id,
            assistant_id=assistant_id,
            created_at=self.clock.now(),
        )
