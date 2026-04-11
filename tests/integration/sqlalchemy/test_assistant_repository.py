from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.integration.sqlalchemy.utils import add_assistant
from tests.unit.assistant.utils import make_assistant

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.assistant.infrastructure.database.postgres.sqlalchemy.repositories.assistant_repository import (
    AssistantRepository,
)


@pytest.mark.asyncio
class TestAssistantRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self, maker: async_sessionmaker[AsyncSession], query_executor: QueryExecutor
    ):
        self.maker = maker
        self.repository = AssistantRepository(query_executor)

    async def test_get_by_id_success(self):
        # Arrange
        assistant = await add_assistant(self.maker)

        # Act
        result = await self.repository.get_by_id(assistant.id)

        # Assert
        assert result.id == assistant.id
        assert result.info.name == assistant.info.name
        assert result.is_deleted is False

    async def test_get_by_id_not_found(self):
        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.repository.get_by_id(AssistantId(uuid4()))

    async def test_add_and_get(self):
        # Arrange
        assistant = make_assistant()

        # Act
        await self.repository.add(assistant)
        loaded = await self.repository.get_by_id(assistant.id)

        # Assert
        assert loaded.id == assistant.id
        assert loaded.info.name == assistant.info.name
        assert loaded.instructions.prompt == assistant.instructions.prompt

    async def test_save_updates_entity(self):
        # Arrange
        assistant = await add_assistant(self.maker)
        assistant.change_name("Updated Name")
        assistant.change_description("Updated Description")

        # Act
        await self.repository.save(assistant)
        loaded = await self.repository.get_by_id(assistant.id)

        # Assert
        assert loaded.info.name == "Updated Name"
        assert loaded.info.description == "Updated Description"

    async def test_get_by_id_does_not_return_soft_deleted(self):
        # Arrange
        assistant = await add_assistant(self.maker)
        assistant.delete()
        await self.repository.save(assistant)

        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.repository.get_by_id(assistant.id)
