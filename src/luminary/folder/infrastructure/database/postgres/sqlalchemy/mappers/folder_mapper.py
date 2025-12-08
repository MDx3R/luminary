from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assisnant import AssistantId
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.folder.domain.value_objects.folder_info import FolderInfo
from luminary.folder.infrastructure.database.postgres.sqlalchemy.models.folder_base import (
    FolderBase,
    FolderChatBase,
    FolderSourceBase,
)
from luminary.source.domain.entity.source import SourceId


class FolderMapper:
    @classmethod
    def to_domain(cls, base: FolderBase) -> Folder:
        chats = {ChatId(c.chat_id) for c in base.chats}
        sources = {SourceId(s.source_id) for s in base.sources}

        assistant_id = None
        if base.assistant_id:
            assistant_id = AssistantId(base.assistant_id)

        return Folder(
            id=FolderId(base.folder_id),
            owner_id=UserId(base.user_id),
            info=FolderInfo(base.name, base.description),
            assistant_id=assistant_id,
            created_at=DateTime(base.created_at),
            _chats=chats,
            _sources=sources,
        )

    @classmethod
    def to_persistence(cls, folder: Folder) -> FolderBase:
        folder_id = folder.id.value

        chats: list[FolderChatBase] = []
        for chat_id in folder.chats:
            chats.append(FolderChatBase(folder_id=folder_id, chat_id=chat_id.value))
        sources: list[FolderSourceBase] = []
        for source_id in folder.sources:
            sources.append(
                FolderSourceBase(folder_id=folder_id, source_id=source_id.value)
            )

        assistant_id = None
        if folder.assistant_id:
            assistant_id = folder.assistant_id.value

        return FolderBase(
            folder_id=folder_id,
            user_id=folder.owner_id.value,
            name=folder.info.name,
            description=folder.info.description,
            assistant_id=assistant_id,
            created_at=folder.created_at.value,
            chats=chats,
            sources=sources,
        )
