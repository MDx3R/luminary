from common.domain.value_objects.datetime import DateTime

from luminary.folder.domain.entity.folder import Folder, FolderInfo
from luminary.folder.infrastructure.database.postgres.sqlalchemy.models.folder_base import (
    FolderBase,
    FolderChatBase,
    FolderSourceBase,
)


class FolderMapper:
    @classmethod
    def to_domain(cls, base: FolderBase) -> Folder:
        chats = {c.chat_id for c in base.chats}
        sources = {s.source_id for s in base.sources}

        return Folder(
            folder_id=base.folder_id,
            user_id=base.user_id,
            info=FolderInfo(base.name, base.description),
            model_id=base.model_id,
            assistant_id=base.assistant_id,
            created_at=DateTime(base.created_at),
            _chats=chats,
            _sources=sources,
        )

    @classmethod
    def to_persistence(cls, folder: Folder) -> FolderBase:
        chats: list[FolderChatBase] = []
        for chat_id in folder.chats:
            chats.append(FolderChatBase(folder_id=folder.folder_id, chat_id=chat_id))
        sources: list[FolderSourceBase] = []
        for source_id in folder.sources:
            sources.append(
                FolderSourceBase(folder_id=folder.folder_id, source_id=source_id)
            )

        return FolderBase(
            folder_id=folder.folder_id,
            user_id=folder.user_id,
            name=folder.info.name,
            description=folder.info.description,
            model_id=folder.model_id,
            assistant_id=folder.assistant_id,
            created_at=folder.created_at.value,
            chats=chats,
            sources=sources,
        )
