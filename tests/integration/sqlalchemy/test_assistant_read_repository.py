"""Integration tests for AssistantReadRepository."""

from uuid import UUID, uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from tests.integration.sqlalchemy.utils import add_assistant, persist_assistant
from tests.unit.assistant.utils import make_assistant

from luminary.assistant.domain.entity.assistant import Assistant
from luminary.assistant.infrastructure.database.postgres.sqlalchemy.repositories.assistant_read_repository import (
    AssistantReadRepository,
)


@pytest.mark.asyncio
class TestAssistantReadRepository:
    @pytest.fixture(autouse=True)
    def setup(self, maker, query_executor: QueryExecutor) -> None:
        self.maker = maker
        self.read_repo = AssistantReadRepository(query_executor)

    async def _add_assistant(self, owner_id: UUID | None = None) -> Assistant:
        owner_id = owner_id or uuid4()
        return await add_assistant(
            maker=self.maker, user_id=owner_id, name="Test", description="Desc"
        )

    # --- get_by_id ---

    async def test_get_by_id_returns_read_model(self) -> None:
        # Arrange
        assistant = await self._add_assistant()
        owner_id = assistant.owner_id.value

        # Act
        result = await self.read_repo.get_by_id(assistant.id.value, owner_id)

        # Assert
        assert result.id == assistant.id.value
        assert result.name == assistant.info.name
        assert result.description == assistant.info.description
        assert result.type == assistant.type.value
        assert result.prompt == assistant.instructions.prompt

    async def test_get_by_id_not_found_raises(self) -> None:
        # Arrange
        owner_id = uuid4()

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.read_repo.get_by_id(uuid4(), owner_id)

    async def test_get_by_id_wrong_owner_raises(self) -> None:
        # Arrange
        assistant = await self._add_assistant()
        other_owner = uuid4()
        assert other_owner != assistant.owner_id.value

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.read_repo.get_by_id(assistant.id.value, other_owner)

    async def test_get_by_id_soft_deleted_raises(self) -> None:
        # Arrange
        owner_id = uuid4()
        assistant = make_assistant(user_id=owner_id)
        assistant.delete()
        await persist_assistant(self.maker, assistant)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.read_repo.get_by_id(assistant.id.value, assistant.owner_id.value)

    # --- list_by_owner ---

    async def test_list_by_owner_empty(self) -> None:
        # Arrange
        owner_id = uuid4()

        # Act
        result = await self.read_repo.list_by_owner(owner_id)

        # Assert
        assert list(result) == []

    async def test_list_by_owner_returns_summaries_ordered_by_created_at_desc(
        self,
    ) -> None:
        # Arrange
        owner_id = uuid4()
        assistant1 = await add_assistant(self.maker, user_id=owner_id, name="A1")
        assistant2 = await add_assistant(self.maker, user_id=owner_id, name="A2")

        # Act
        result = await self.read_repo.list_by_owner(owner_id)

        # Assert
        assert {r.id for r in result} == {a.id.value for a in [assistant1, assistant2]}
        assert {r.name for r in result} == {"A1", "A2"}

    async def test_list_by_owner_excludes_other_owner(self) -> None:
        # Arrange
        owner_a = uuid4()
        owner_b = uuid4()
        await self._add_assistant(owner_id=owner_a)

        # Act
        result = await self.read_repo.list_by_owner(owner_b)

        # Assert
        assert list(result) == []

    async def test_list_by_owner_excludes_soft_deleted(self) -> None:
        # Arrange
        owner_id = uuid4()
        assistant = make_assistant(user_id=owner_id)
        assistant.delete()
        await persist_assistant(self.maker, assistant)

        # Act
        result = await self.read_repo.list_by_owner(owner_id)

        # Assert
        assert list(result) == []
