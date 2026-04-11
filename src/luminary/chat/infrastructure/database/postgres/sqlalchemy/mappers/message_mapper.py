from common.domain.value_objects.datetime import DateTime

from luminary.chat.application.dtos.read_models import (
    AttachmentReadModel,
    MessageReadModel,
)
from luminary.chat.domain.entity.attachment import Attachment
from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.message_id import MessageId
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.message_base import (
    MessageBase,
)
from luminary.model.domain.entity.model import ModelId


class MessageMapper:
    @classmethod
    def to_domain(cls, base: MessageBase) -> Message:
        atts = list[Attachment]()
        return Message(
            id=MessageId(base.message_id),
            chat_id=ChatId(base.chat_id),
            role=base.role,
            status=base.status,
            content=base.content or "",
            model_id=ModelId(base.model_id),
            edited_at=DateTime(base.edited_at),
            created_at=DateTime(base.created_at),
            tokens=base.tokens,
            _attachments=set[Attachment](atts),
        )

    @classmethod
    def to_persistence(cls, message: Message) -> MessageBase:
        return MessageBase(
            message_id=message.id.value,
            chat_id=message.chat_id.value,
            role=message.role,
            status=message.status,
            content=message.content,
            model_id=message.model_id.value,
            tokens=message.tokens,
            edited_at=message.edited_at.value,
            created_at=message.created_at.value,
            updated_at=message.edited_at.value,
        )


class MessageReadMapper:
    @classmethod
    def to_read(cls, base: MessageBase) -> MessageReadModel:
        attachments = [
            AttachmentReadModel(
                name=a.name, content_id=a.content_id, source_id=a.source_id
            )
            for a in base.attachments
        ]
        return MessageReadModel(
            id=base.message_id,
            chat_id=base.chat_id,
            role=base.role.value,
            status=base.status.value,
            content=base.content,
            model_id=base.model_id,
            tokens=base.tokens,
            created_at=base.created_at,
            edited_at=base.edited_at,
            attachments=attachments,
        )
