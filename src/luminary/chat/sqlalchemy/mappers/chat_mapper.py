from common.domain.value_objects.datetime import DateTime

from luminary.chat.domain.entity.chat import Chat
from luminary.chat.sqlalchemy.models.chat_base import ChatBase


class ChatMapper:
    @classmethod
    def to_domain(cls, base: ChatBase) -> Chat:
        return Chat(
            chat_id=base.chat_id,
            user_id=base.user_id,
            folder_id=base.folder_id,
            name=base.name,
            created_at=DateTime(base.created_at),
        )

    @classmethod
    def to_persistence(cls, chat: Chat) -> ChatBase:
        return ChatBase(
            chat_id=chat.chat_id,
            user_id=chat.user_id,
            folder_id=chat.folder_id,
            name=chat.name,
            created_at=chat.created_at.value,
        )
