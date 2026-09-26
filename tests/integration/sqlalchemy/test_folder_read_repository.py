"""Integration tests for FolderReadRepository."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.domain.value_objects.datetime import DateTime
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from tests.integration.sqlalchemy.utils import (
    add_assistant,
    add_folder,
    persist_chat,
    persist_folder,
    persist_source,
)
from tests.unit.chat.utils import make_chat
from tests.unit.folder.utils import make_folder
from tests.unit.source.utils import make_file_source, make_link_source, make_page_source

from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.infrastructure.database.postgres.sqlalchemy.repositories.folder_read_repository import (
    FolderReadRepository,
)
from luminary.source.domain.entity.file_source import FileSource
from luminary.source.domain.entity.link_source import LinkSource
from luminary.source.domain.entity.page_source import PageSource
from luminary.source.domain.entity.source import Source, SourceId


@pytest.mark.asyncio
class TestFolderReadRepository:
    @pytest.fixture(autouse=True)
    def setup(self, maker, query_executor: QueryExecutor) -> None:
        self.maker = maker
        self.read_repo = FolderReadRepository(query_executor)

    async def _add_folder(self, owner_id: UUID | None = None) -> Folder:
        owner_id = owner_id or uuid4()
        return await add_folder(self.maker, owner_id=owner_id)

    # --- get_by_id ---

    async def test_get_by_id_returns_read_model_minimal(self) -> None:
        # Arrange
        folder = await self._add_folder()
        owner_id = folder.owner_id.value

        # Act
        result = await self.read_repo.get_by_id(folder.id.value, owner_id)

        # Assert
        assert result.id == folder.id.value
        assert result.name == folder.info.name
        assert result.description == folder.info.description
        assert result.assistant_id is None
        assert result.assistant_name is None
        assert result.editor is None
        assert result.chats == []
        assert result.sources == []

    async def test_get_by_id_with_editor_returns_editor_item(self) -> None:
        # Arrange
        folder = make_folder(owner_id=uuid4())
        folder.update_editor_content(
            "Editor text",
            DateTime(datetime.now(UTC)),
        )
        await persist_folder(self.maker, folder)
        owner_id = folder.owner_id.value

        # Act
        result = await self.read_repo.get_by_id(folder.id.value, owner_id)

        # Assert
        assert result.editor is not None
        assert result.editor.text == "Editor text"

    @pytest.mark.parametrize(
        "source", [make_file_source(), make_page_source(), make_link_source()]
    )
    async def test_get_by_id_with_chats_and_sources_returns_items(
        self, source: Source
    ) -> None:
        # Arrange
        owner_id = source.owner_id.value
        await persist_source(self.maker, source)
        chat = make_chat(user_id=owner_id)
        await persist_chat(self.maker, chat)
        folder = make_folder(owner_id=owner_id)
        folder.add_chat(ChatId(chat.id.value))
        folder.add_source(SourceId(source.id.value))
        await persist_folder(self.maker, folder)

        # Act
        result = await self.read_repo.get_by_id(folder.id.value, owner_id)

        # Assert
        assert [c.id for c in result.chats] == [chat.id.value]
        assert result.chats[0].name == chat.info.name
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

    async def test_get_by_id_with_assistant_returns_assistant_name(
        self,
    ) -> None:
        # Arrange
        owner_id = uuid4()
        assistant = await add_assistant(
            self.maker, user_id=owner_id, name="Folder Assistant"
        )
        folder = await add_folder(
            self.maker, owner_id=owner_id, assistant_id=assistant.id.value
        )

        # Act
        result = await self.read_repo.get_by_id(folder.id.value, owner_id)

        # Assert
        assert result.assistant_id == assistant.id.value
        assert result.assistant_name == "Folder Assistant"

    async def test_get_by_id_not_found_raises(self) -> None:
        # Arrange
        owner_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.read_repo.get_by_id(uuid4(), owner_id)

    async def test_get_by_id_wrong_owner_raises(self) -> None:
        # Arrange
        folder = await self._add_folder()
        other_owner = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.read_repo.get_by_id(folder.id.value, other_owner)

    async def test_get_by_id_soft_deleted_raises(self) -> None:
        # Arrange
        folder = make_folder(owner_id=uuid4())
        folder.delete()
        await persist_folder(self.maker, folder)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.read_repo.get_by_id(folder.id.value, folder.owner_id.value)

    # --- list_by_owner ---

    async def test_list_by_owner_empty(self) -> None:
        # Act
        result = await self.read_repo.list_by_owner(uuid4())

        # Assert
        assert list(result) == []

    async def test_list_by_owner_returns_summaries_ordered_by_created_at_desc(
        self,
    ) -> None:
        # Arrange
        owner_id = uuid4()
        f1 = await add_folder(self.maker, owner_id=owner_id)
        f2 = await add_folder(self.maker, owner_id=owner_id)

        # Act
        result = await self.read_repo.list_by_owner(owner_id)

        # Assert
        assert {r.id for r in result} == {f1.id.value, f2.id.value}
        assert {r.name for r in result} == {f1.info.name, f2.info.name}
        assert result[0].created_at >= result[1].created_at

    async def test_list_by_owner_excludes_other_owner(self) -> None:
        # Arrange
        owner_a = uuid4()
        await self._add_folder(owner_id=owner_a)

        # Act
        result = await self.read_repo.list_by_owner(uuid4())

        # Assert
        assert list(result) == []

    async def test_list_by_owner_excludes_soft_deleted(self) -> None:
        # Arrange
        owner_id = uuid4()
        folder = make_folder(owner_id=owner_id)
        folder.delete()
        await persist_folder(self.maker, folder)

        # Act
        result = await self.read_repo.list_by_owner(owner_id)

        # Assert
        assert list(result) == []
