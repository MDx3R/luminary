"""Integration tests for ChatReadRepository."""

from uuid import UUID, uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from tests.integration.sqlalchemy.utils import (
    add_assistant,
    add_chat,
    add_message,
    persist_chat,
    persist_source,
)
from tests.unit.chat.utils import make_chat
from tests.unit.source.utils import make_file_source, make_link_source, make_page_source

from luminary.chat.domain.entity.chat import Chat
from luminary.chat.domain.entity.message import Message
from luminary.chat.infrastructure.database.postgres.sqlalchemy.models.attachment_base import (
    AttachmentBase,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.repositories.chat_read_repository import (
    ChatReadRepository,
)
from luminary.source.domain.entity.file_source import FileSource
from luminary.source.domain.entity.link_source import LinkSource
from luminary.source.domain.entity.page_source import PageSource
from luminary.source.domain.entity.source import Source, SourceId


@pytest.mark.asyncio
class TestChatReadRepository:
    @pytest.fixture(autouse=True)
    def setup(self, maker, query_executor: QueryExecutor) -> None:
        self.maker = maker
        self.query_executor = query_executor
        self.read_repo = ChatReadRepository(query_executor)

    async def _add_chat(
        self, owner_id: UUID | None = None, folder_id=None, assistant_id=None
    ) -> Chat:
        owner_id = owner_id or uuid4()
        return await add_chat(
            self.maker,
            user_id=owner_id,
            folder_id=folder_id,
            assistant_id=assistant_id,
        )

    async def _add_message(self, chat_id, content="Msg") -> Message:
        return await add_message(self.maker, chat_id=chat_id, content=content)

    # --- get_by_id ---

    async def test_get_by_id_returns_read_model_no_sources_no_assistant(
        self,
    ) -> None:
        # Arrange
        chat = await self._add_chat()
        owner_id = chat.owner_id.value

        # Act
        result = await self.read_repo.get_by_id(chat.id.value, owner_id)

        # Assert
        assert result.id == chat.id.value
        assert result.name == chat.info.name
        assert result.folder_id is None
        assert result.assistant_id is None
        assert result.assistant_name is None
        assert result.sources == []

    @pytest.mark.parametrize(
        "source", [make_file_source(), make_page_source(), make_link_source()]
    )
    async def test_get_by_id_with_sources_returns_source_items(
        self, source: Source
    ) -> None:
        # Arrange
        owner_id = source.owner_id.value
        await persist_source(self.maker, source)
        chat = make_chat(user_id=owner_id)
        chat.add_source(SourceId(source.id.value))
        await persist_chat(self.maker, chat)

        # Act
        result = await self.read_repo.get_by_id(chat.id.value, owner_id)

        # Assert
        assert [s.id for s in result.sources] == [source.id.value]
        assert result.sources[0].title == source.title.value
        assert result.sources[0].type == source.type.value
        match source:
            case FileSource():
                assert result.sources[0].file_id == source.file_id.value
            case PageSource():
                assert result.sources[0].editable == source.editable
            case LinkSource():
                assert result.sources[0].url == source.url.value

    async def test_get_by_id_with_assistant_returns_assistant_name(self) -> None:
        # Arrange
        owner_id = uuid4()
        assistant = await add_assistant(
            self.maker, user_id=owner_id, name="My Assistant"
        )
        chat = await add_chat(
            self.maker, user_id=owner_id, assistant_id=assistant.id.value
        )

        # Act
        result = await self.read_repo.get_by_id(chat.id.value, owner_id)

        # Assert
        assert result.assistant_id == assistant.id.value
        assert result.assistant_name == "My Assistant"

    async def test_get_by_id_not_found_raises(self) -> None:
        # Arrange
        owner_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.read_repo.get_by_id(uuid4(), owner_id)

    async def test_get_by_id_wrong_owner_raises(self) -> None:
        # Arrange
        chat = await self._add_chat()
        other_owner = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.read_repo.get_by_id(chat.id.value, other_owner)

    async def test_get_by_id_soft_deleted_raises(self) -> None:
        # Arrange
        owner_id = uuid4()
        chat = make_chat(user_id=owner_id)
        chat.delete()
        await persist_chat(self.maker, chat)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.read_repo.get_by_id(chat.id.value, chat.owner_id.value)

    # --- list_standalone_by_owner ---

    async def test_list_standalone_by_owner_empty(self) -> None:
        # Act
        result = await self.read_repo.list_standalone_by_owner(uuid4())

        # Assert
        assert list(result) == []

    async def test_list_standalone_by_owner_returns_only_standalone_chats(
        self,
    ) -> None:
        # Arrange
        owner_id = uuid4()
        standalone = await self._add_chat(owner_id=owner_id, folder_id=None)
        folder_id = uuid4()
        await self._add_chat(owner_id=owner_id, folder_id=folder_id)

        # Act
        result = await self.read_repo.list_standalone_by_owner(owner_id)

        # Assert
        assert {r.id for r in result} == {standalone.id.value}

    async def test_list_standalone_by_owner_excludes_other_owner(self) -> None:
        # Arrange
        owner_a = uuid4()
        await self._add_chat(owner_id=owner_a)

        # Act
        result = await self.read_repo.list_standalone_by_owner(uuid4())

        # Assert
        assert list(result) == []

    async def test_list_standalone_by_owner_excludes_soft_deleted(self) -> None:
        # Arrange
        owner_id = uuid4()
        chat = make_chat(user_id=owner_id)
        chat.delete()
        await persist_chat(self.maker, chat)

        # Act
        result = await self.read_repo.list_standalone_by_owner(owner_id)

        # Assert
        assert list(result) == []

    # --- list_messages ---

    async def test_list_messages_empty(self) -> None:
        # Arrange
        chat = await self._add_chat()

        # Act
        result = await self.read_repo.list_messages(chat.id.value, chat.owner_id.value)

        # Assert
        assert list(result) == []

    async def test_list_messages_returns_ordered_by_created_at_desc(self) -> None:
        # Arrange
        chat = await self._add_chat()
        m1 = await self._add_message(chat.id.value, "First")
        m2 = await self._add_message(chat.id.value, "Second")
        m3 = await self._add_message(chat.id.value, "Third")

        # Act
        result = await self.read_repo.list_messages(
            chat.id.value, chat.owner_id.value, limit=10
        )

        # Assert
        assert [r.id for r in result] == [m3.id.value, m2.id.value, m1.id.value]
        assert [r.content for r in result] == ["Third", "Second", "First"]

    async def test_list_messages_respects_limit(self) -> None:
        # Arrange
        chat = await self._add_chat()
        await self._add_message(chat.id.value, "A")
        await self._add_message(chat.id.value, "B")
        m3 = await self._add_message(chat.id.value, "C")

        # Act
        result = await self.read_repo.list_messages(
            chat.id.value, chat.owner_id.value, limit=2
        )

        # Assert (desc order: C, B)
        assert [r.content for r in result] == ["C", "B"]
        assert result[0].id == m3.id.value

    async def test_list_messages_before_cursor(self) -> None:
        # Arrange
        chat = await self._add_chat()
        m1 = await self._add_message(chat.id.value, "First")
        m2 = await self._add_message(chat.id.value, "Second")
        m3 = await self._add_message(chat.id.value, "Third")

        # Act
        result = await self.read_repo.list_messages(
            chat.id.value,
            chat.owner_id.value,
            limit=10,
            before=m3.id.value,
        )

        # Assert
        assert {r.id for r in result} == {m1.id.value, m2.id.value}
        assert {r.content for r in result} == {"First", "Second"}

    async def test_list_messages_wrong_owner_returns_empty(self) -> None:
        # Arrange
        chat = await self._add_chat()
        await self._add_message(chat.id.value, "Hi")
        wrong_owner = uuid4()

        # Act
        result = await self.read_repo.list_messages(chat.id.value, wrong_owner)

        # Assert
        assert list(result) == []

    async def test_list_messages_with_attachments(self) -> None:
        # Arrange
        chat = await self._add_chat()
        message = await self._add_message(chat.id.value, "With attachment")
        att = AttachmentBase(
            message_id=message.id.value,
            name="file.pdf",
            content_id=uuid4(),
            source_id=None,
        )
        await self.query_executor.add(att)

        # Act
        result = await self.read_repo.list_messages(chat.id.value, chat.owner_id.value)

        # Assert
        assert {r.id for r in result} == {message.id.value}
        assert len(result[0].attachments) == 1
        assert result[0].attachments[0].name == "file.pdf"
