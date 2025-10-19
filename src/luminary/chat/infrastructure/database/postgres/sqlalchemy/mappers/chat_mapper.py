from common.domain.value_objects.datetime import DateTime

from luminary.chat.domain.entity.chat import Chat, ChatInfo, ChatSettings
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.chat_base import (
    ChatBase,
)


class ChatMapper:
    @classmethod
    def to_domain(cls, base: ChatBase) -> Chat:
        return Chat(
            chat_id=base.chat_id,
            user_id=base.user_id,
            folder_id=base.folder_id,
            info=ChatInfo(name=base.name),
            settings=ChatSettings(
                model_id=base.model_id,
                system_prompt=base.system_prompt,
                max_context_messages=base.max_context_messages,
            ),
            created_at=DateTime(base.created_at),
        )

    @classmethod
    def to_persistence(cls, chat: Chat) -> ChatBase:
        return ChatBase(
            chat_id=chat.chat_id,
            user_id=chat.user_id,
            folder_id=chat.folder_id,
            name=chat.info.name,
            model_id=chat.settings.model_id,
            system_prompt=chat.settings.system_prompt,
            max_context_messages=chat.settings.max_context_messages,
            created_at=chat.created_at.value,
        )
