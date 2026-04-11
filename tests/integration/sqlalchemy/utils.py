from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.unit.assistant.utils import make_assistant
from tests.unit.chat.utils import make_chat, make_message
from tests.unit.folder.utils import make_folder
from tests.unit.source.utils import (
    make_file_source,
    make_link_source,
    make_page_source,
    make_source,
)

from luminary.assistant.domain.entity.assistant import Assistant
from luminary.assistant.infrastructure.database.postgres.sqlalchemy.mappers.assistant_mapper import (
    AssistantMapper,
)
from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.entity.message import Message
from luminary.chat.infrastructure.database.postgres.sqlalchemy.mappers.chat_mapper import (
    ChatMapper,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.mappers.message_mapper import (
    MessageMapper,
)
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.infrastructure.database.postgres.sqlalchemy.mappers.folder_mapper import (
    FolderMapper,
)
from luminary.source.domain.entity.file_source import FileSource
from luminary.source.domain.entity.link_source import LinkSource
from luminary.source.domain.entity.page_source import PageSource
from luminary.source.domain.entity.source import Source
from luminary.source.infrastructure.database.postgres.sqlalchemy.mappers.source_mapper import (
    SourceMapper,
)


async def persist_source(
    maker: async_sessionmaker[AsyncSession], source: Source
) -> None:
    async with maker() as session:
        model = SourceMapper.to_persistence(source)
        session.add(model)
        await session.commit()


async def add_source(
    maker: async_sessionmaker[AsyncSession], **kwargs: Any
) -> Source:
    source = make_source(**kwargs)
    await persist_source(maker, source)
    return source


async def add_file_source(
    maker: async_sessionmaker[AsyncSession], **kwargs: Any
) -> FileSource:
    source = make_file_source(**kwargs)
    await persist_source(maker, source)
    return source


async def add_link_source(
    maker: async_sessionmaker[AsyncSession], **kwargs: Any
) -> LinkSource:
    source = make_link_source(**kwargs)
    await persist_source(maker, source)
    return source


async def add_page_source(
    maker: async_sessionmaker[AsyncSession], **kwargs: Any
) -> PageSource:
    source = make_page_source(**kwargs)
    await persist_source(maker, source)
    return source


async def persist_assistant(
    maker: async_sessionmaker[AsyncSession], assistant: Assistant
) -> None:
    async with maker() as session:
        model = AssistantMapper.to_persistence(assistant)
        session.add(model)
        await session.commit()


async def add_assistant(
    maker: async_sessionmaker[AsyncSession], **kwargs: Any
) -> Assistant:
    assistant = make_assistant(**kwargs)
    await persist_assistant(maker, assistant)
    return assistant


async def persist_chat(
    maker: async_sessionmaker[AsyncSession], chat: Chat
) -> None:
    async with maker() as session:
        model = ChatMapper.to_persistence(chat)
        session.add(model)
        await session.commit()


async def add_chat(
    maker: async_sessionmaker[AsyncSession], **kwargs: Any
) -> Chat:
    chat = make_chat(**kwargs)
    await persist_chat(maker, chat)
    return chat


async def persist_message(
    maker: async_sessionmaker[AsyncSession], message: Message
) -> None:
    async with maker() as session:
        model = MessageMapper.to_persistence(message)
        session.add(model)
        await session.commit()


async def add_message(
    maker: async_sessionmaker[AsyncSession], **kwargs: Any
) -> Message:
    message = make_message(**kwargs)
    await persist_message(maker, message)
    return message


async def persist_folder(
    maker: async_sessionmaker[AsyncSession], folder: Folder
) -> None:
    async with maker() as session:
        model = FolderMapper.to_persistence(folder)
        session.add(model)
        await session.commit()


async def add_folder(
    maker: async_sessionmaker[AsyncSession], **kwargs: Any
) -> Folder:
    folder = make_folder(**kwargs)
    await persist_folder(maker, folder)
    return folder

