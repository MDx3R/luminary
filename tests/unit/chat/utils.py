from datetime import UTC, datetime
from uuid import UUID, uuid4

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId


from luminary.assistant.domain.entity.assisnant import AssistantId
from luminary.chat.application.interfaces.usecases.query.get_chat_use_case import (
    ChatDTO,
)
from luminary.chat.application.interfaces.usecases.query.get_user_chats_use_case import (
    ChatListItemDTO,
)
from luminary.chat.domain.entity.chat import Chat, ChatInfo, ChatSettings
from luminary.chat.domain.entity.message import Message
from luminary.chat.domain.enums import Author, MessageStatus
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.chat.domain.value_objects.chat_info import ChatInfo
from luminary.chat.domain.value_objects.chat_settings import ChatSettings
from luminary.chat.domain.value_objects.message_id import MessageId
from luminary.folder.domain.entity.folder import FolderId
from luminary.model.domain.entity.model import ModelId


def make_chat(  # noqa: PLR0913
    *,
    chat_id: UUID | None = None,
    user_id: UUID | None = None,
    folder_id: UUID | None = None,
    model_id: UUID | None = None,
    assistant_id: UUID | None = None,
    settings: ChatSettings | None = None,
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
        settings=settings or make_chat_settings(model_id=model_id),
    )


def make_chat_settings(
    *, model_id: UUID | None = None, max_context_messages: int = 10
) -> ChatSettings:
    return ChatSettings(
        model_id=ModelId(model_id or uuid4()),
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
    message_id = message_id or uuid4()
    chat_id = chat_id or uuid4()
    model_id = model_id or uuid4()
    return Message(
        id=MessageId(message_id),
        chat_id=ChatId(chat_id),
        model_id=ModelId(model_id),
        content=content,
        role=role or Author.USER,
        status=status or MessageStatus.COMPLETED,
        created_at=DateTime(datetime.now(UTC)),
        edited_at=DateTime(datetime.now(UTC)),
    )


def make_chat_dto(  # noqa: PLR0913
    *,
    chat_id: UUID | None = None,
    user_id: UUID | None = None,
    folder_id: UUID | None = None,
    name: str = "Test Chat",
    model_id: UUID | None = None,
    system_prompt: str = "Test prompt",
    max_context_messages: int = 10,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> ChatDTO:
    return ChatDTO(
        chat_id=chat_id or uuid4(),
        user_id=user_id or uuid4(),
        folder_id=folder_id,
        name=name,
        model_id=model_id or uuid4(),
        system_prompt=system_prompt,
        max_context_messages=max_context_messages,
        created_at=created_at or datetime.now(UTC),
        updated_at=updated_at or datetime.now(UTC),
    )


def make_chat_list_item_dto(
    *,
    chat_id: UUID | None = None,
    name: str = "Test Chat",
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> ChatListItemDTO:
    return ChatListItemDTO(
        chat_id=chat_id or uuid4(),
        name=name,
        created_at=created_at or datetime.now(UTC),
        updated_at=updated_at or datetime.now(UTC),
    )
