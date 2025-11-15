from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId

from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.chat_info import ChatInfo
from luminary.chat.domain.value_objects.chat_settings import ChatSettings
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.chat_base import (
    ChatBase,
    ChatSourceBase,
)
from luminary.folder.domain.entity.folder import FolderId
from luminary.model.domain.entity.model import ModelId
from luminary.source.domain.entity.source import SourceId


class ChatMapper:
    @classmethod
    def to_domain(cls, base: ChatBase) -> Chat:
        sources = {SourceId(s.source_id) for s in base.sources}

        return Chat(
            id=ChatId(base.chat_id),
            owner_id=UserId(base.user_id),
            folder_id=FolderId(base.folder_id) if base.folder_id else None,
            info=ChatInfo(name=base.name),
            settings=ChatSettings(
                model_id=ModelId(base.model_id),
                system_prompt=base.system_prompt,
                max_context_messages=base.max_context_messages,
            ),
            created_at=DateTime(base.created_at),
            _sources=sources,
        )

    @classmethod
    def to_persistence(cls, chat: Chat) -> ChatBase:
        chat_id = chat.id.value

        sources: list[ChatSourceBase] = []
        for source_id in chat.sources:
            sources.append(ChatSourceBase(chat_id=chat_id, source_id=source_id.value))

        return ChatBase(
            chat_id=chat_id,
            user_id=chat.owner_id.value,
            folder_id=chat.folder_id.value if chat.folder_id else None,
            name=chat.info.name,
            model_id=chat.settings.model_id.value,
            system_prompt=chat.settings.system_prompt,
            max_context_messages=chat.settings.max_context_messages,
            created_at=chat.created_at.value,
            sources=sources,
        )
