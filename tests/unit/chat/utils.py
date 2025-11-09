from datetime import UTC, datetime
from uuid import UUID, uuid4

from common.domain.value_objects.datetime import DateTime

from luminary.chat.domain.entity.chat import Chat, ChatInfo, ChatSettings
from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.enums import Author, MessageStatus


def make_chat(  # noqa: PLR0913
    *,
    chat_id: UUID | None = None,
    user_id: UUID | None = None,
    folder_id: UUID | None = None,
    model_id: UUID | None = None,
    settings: ChatSettings | None = None,
    name: str = "Test Chat",
) -> Chat:
    return Chat(
        chat_id=chat_id or uuid4(),
        user_id=user_id or uuid4(),
        folder_id=folder_id or uuid4(),
        created_at=DateTime(datetime.now(UTC)),
        info=ChatInfo(name=name),
        settings=settings or make_chat_settings(model_id=model_id),
    )


def make_chat_settings(
    *,
    model_id: UUID | None = None,
    system_prompt: str = "Test prompt",
    max_context_messages: int = 10,
) -> ChatSettings:
    return ChatSettings(
        model_id=model_id or uuid4(),
        system_prompt=system_prompt,
        max_context_messages=max_context_messages,
    )


def make_message(  # noqa: PLR0913
    *,
    message_id: UUID | None = None,
    chat_id: UUID | None = None,
    model_id: UUID | None = None,
    content: str = "Test message",
    role: Author | None = None,
    status: MessageStatus | None = None,
) -> Message:
    return Message(
        message_id=message_id or uuid4(),
        chat_id=chat_id or uuid4(),
        model_id=model_id or uuid4(),
        content=content,
        role=role or Author.USER,
        status=status or MessageStatus.COMPLETED,
        created_at=DateTime(datetime.now(UTC)),
        edited_at=DateTime(datetime.now(UTC)),
    )
