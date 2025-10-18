from common.domain.value_objects.datetime import DateTime

from luminary.folder.domain.entity.folder import Folder, FolderInfo
from luminary.folder.infrastructure.database.postgres.sqlalchemy.models.folder_base import (
    FolderBase,
)


class FolderMapper:
    @classmethod
    def to_domain(cls, base: FolderBase) -> Folder:
        return Folder(
            folder_id=base.folder_id,
            user_id=base.user_id,
            info=FolderInfo(base.name, base.description),
            model_id=base.model_id,
            assistant_id=base.assistant_id,
            created_at=DateTime(base.created_at),
            _chats=set(),
            _files=set(),
        )

    @classmethod
    def to_persistence(cls, folder: Folder) -> FolderBase:
        return FolderBase(
            folder_id=folder.folder_id,
            user_id=folder.user_id,
            name=folder.info.name,
            description=folder.info.description,
            model_id=folder.model_id,
            assistant_id=folder.assistant_id,
            created_at=folder.created_at.value,
        )
