from datetime import UTC, datetime
from uuid import UUID, uuid4

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.enums import Author, MessageStatus
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.chat_info import ChatInfo
from luminary.chat.domain.value_objects.message_id import MessageId
from luminary.folder.domain.value_objects.folder_id import FolderId


def make_chat(
    *,
    chat_id: UUID | None = None,
    user_id: UUID | None = None,
    folder_id: UUID | None = None,
    assistant_id: UUID | None = None,
    name: str = "Test Chat",
) -> Chat:
    chat_id = chat_id or uuid4()
    user_id = user_id or uuid4()
    return Chat(
        id=ChatId(chat_id),
        owner_id=UserId(user_id),
        folder_id=FolderId(folder_id) if folder_id else None,
        assistant_id=AssistantId(assistant_id) if assistant_id else None,
        created_at=DateTime(datetime.now(UTC)),
        info=ChatInfo(name=name),
        is_deleted=False,
    )


def make_message(
    *,
    message_id: UUID | None = None,
    chat_id: UUID | None = None,
    content: str = "Test message",
    role: Author | None = None,
    status: MessageStatus | None = None,
) -> Message:
    message_id = message_id or uuid4()
    chat_id = chat_id or uuid4()
    return Message(
        id=MessageId(message_id),
        chat_id=ChatId(chat_id),
        content=content,
        role=role or Author.USER,
        status=status or MessageStatus.COMPLETED,
        created_at=DateTime(datetime.now(UTC)),
        edited_at=DateTime(datetime.now(UTC)),
    )
