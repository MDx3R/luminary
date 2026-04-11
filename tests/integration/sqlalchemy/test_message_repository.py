from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.integration.sqlalchemy.utils import add_chat, add_message
from tests.unit.chat.utils import make_message

from luminary.chat.domain.enums import Author, MessageStatus
from luminary.chat.domain.value_objects.message_id import MessageId
from luminary.chat.infrastructure.database.postgres.sqlalchemy.repositories.message_repository import (
    MessageRepository,
)


@pytest.mark.asyncio
class TestMessageReader:
    """Integration tests for MessageRepository as IMessageReader."""

    @pytest.fixture(autouse=True)
    def setup(
        self, maker: async_sessionmaker[AsyncSession], query_executor: QueryExecutor
    ):
        self.maker = maker
        self.message_repository = MessageRepository(query_executor)

    async def _add_chat_and_messages(self, chat_id=None, count: int = 3):
        chat = await add_chat(self.maker, chat_id=chat_id or uuid4())
        messages = []
        for i in range(count):
            msg = await add_message(
                self.maker,
                chat_id=chat.id.value,
                content=f"Message {i}",
                role=Author.USER if i % 2 == 0 else Author.ASSISTANT,
            )
            messages.append(msg)
        return chat, messages

    async def test_get_chat_messages_empty(self):
        # Arrange
        chat = await add_chat(self.maker)

        # Act
        result = await self.message_repository.get_chat_messages(chat.id)

        # Assert
        assert result == []

    async def test_get_chat_messages_returns_in_order(self):
        # Arrange
        _, messages = await self._add_chat_and_messages(count=3)
        chat_id = messages[0].chat_id

        # Act
        result = await self.message_repository.get_chat_messages(chat_id)

        # Assert
        assert [m.id for m in result] == [m.id for m in messages]
        assert [m.content for m in result] == ["Message 0", "Message 1", "Message 2"]

    async def test_get_chat_messages_with_limit(self):
        # Arrange: last N messages (newest in chat). With 5 messages, limit=2
        # returns the 2 most recent in chronological order.
        _, messages = await self._add_chat_and_messages(count=5)
        chat_id = messages[0].chat_id

        # Act
        result = await self.message_repository.get_chat_messages(chat_id, limit=2)

        # Assert
        assert [m.id for m in result] == [m.id for m in messages[-2:]]
        assert [m.content for m in result] == ["Message 3", "Message 4"]

    async def test_get_chat_messages_only_for_given_chat(self):
        # Arrange
        _, messages_a = await self._add_chat_and_messages(count=2)
        await self._add_chat_and_messages(count=2)
        chat_id_a = messages_a[0].chat_id

        # Act
        result = await self.message_repository.get_chat_messages(chat_id_a)

        # Assert
        assert {m.id for m in result} == {m.id for m in messages_a}
        assert all(m.chat_id == chat_id_a for m in result)


@pytest.mark.asyncio
class TestMessageRepository:
    """Integration tests for MessageRepository as IMessageRepository."""

    @pytest.fixture(autouse=True)
    def setup(
        self, maker: async_sessionmaker[AsyncSession], query_executor: QueryExecutor
    ):
        self.maker = maker
        self.repository = MessageRepository(query_executor)

    async def test_get_by_id_success(self) -> None:
        # Arrange
        chat = await add_chat(self.maker)
        message = await add_message(
            self.maker, chat_id=chat.id.value, content="Initial"
        )

        # Act
        result = await self.repository.get_by_id(message.id)

        # Assert
        assert result.id == message.id
        assert result.chat_id == message.chat_id
        assert result.content == message.content
        assert result.role == message.role
        assert result.status == message.status

    async def test_get_by_id_not_found(self):
        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.repository.get_by_id(MessageId(uuid4()))

    async def test_add_and_get(self):
        # Arrange
        chat = await add_chat(self.maker)
        message = make_message(chat_id=chat.id.value, content="Initial")
        await self.repository.add(message)

        # Act
        loaded = await self.repository.get_by_id(message.id)

        # Assert
        assert loaded.id == message.id
        assert loaded.content == message.content
        assert loaded.model_id == message.model_id

    async def test_save_updates_entity(self):
        # Arrange
        chat = await add_chat(self.maker)
        message = await add_message(
            self.maker, chat_id=chat.id.value, content="Initial"
        )
        message.add_chunk(" appended")
        message.complete(tokens=10)

        # Act
        await self.repository.save(message)
        loaded = await self.repository.get_by_id(message.id)

        # Assert
        assert loaded.content == "Initial appended"
        assert loaded.status == MessageStatus.COMPLETED
        assert loaded.tokens == 10  # noqa: PLR2004
