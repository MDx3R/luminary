from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tests.unit.assistant.utils import make_assistant

from luminary.assistant.domain.entity.assisnant import Assistant
from luminary.assistant.infrasturcture.database.postgres.sqlalchemy.mappers.assistant_mapper import (
    AssistantMapper,
)
from luminary.assistant.infrasturcture.database.postgres.sqlalchemy.models.assistant_base import (
    AssistantBase,
)
from luminary.assistant.infrasturcture.database.postgres.sqlalchemy.repositories.assistant_repository import (
    AssistantRepository,
)


@pytest.mark.asyncio
class TestAssistantRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self, maker: async_sessionmaker[AsyncSession], query_executor: QueryExecutor
    ):
        self.maker = maker
        self.assistant_repository = AssistantRepository(query_executor)

    async def _exists(self, assistant: Assistant) -> bool:
        async with self.maker() as session:
            result = await session.get(AssistantBase, assistant.assistant_id)
            return result is not None

    async def _get(self, assistant: Assistant) -> Assistant | None:
        async with self.maker() as session:
            result = await session.get(AssistantBase, assistant.assistant_id)
            if not result:
                return None
            return AssistantMapper.to_domain(result)

    async def _add_assistant(self) -> Assistant:
        assistant = make_assistant(name="Test Assistant")
        async with self.maker() as session:
            session.add(AssistantMapper.to_persistence(assistant))
            await session.commit()
        return assistant

    async def test_get_assistant_success(self):
        # Arrange
        assistant = await self._add_assistant()

        # Act
        result = await self.assistant_repository.get_by_id(assistant.assistant_id)

        # Assert
        assert result == assistant

    async def test_get_assistant_not_found(self):
        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.assistant_repository.get_by_id(uuid4())

    async def test_get_assistant_exists_by_name_for_user_true(self):
        # Arrange
        assistant = await self._add_assistant()

        # Act
        result = await self.assistant_repository.exists_by_name_for_user(
            assistant.name, assistant.user_id
        )

        # Assert
        assert result is True

    async def test_get_assistant_exists_by_name_for_user_false_no_name(self):
        # Arrange
        assistant = await self._add_assistant()

        # Act
        result = await self.assistant_repository.exists_by_name_for_user(
            "Random Name", assistant.user_id
        )

        # Assert
        assert result is False

    async def test_get_assistant_exists_by_name_for_user_false_no_user(self):
        # Arrange
        assistant = await self._add_assistant()

        # Act
        result = await self.assistant_repository.exists_by_name_for_user(
            assistant.name, uuid4()
        )

        # Assert
        assert result is False

    async def test_add_success(self):
        # Arrange
        assistant = make_assistant(name="Test Assistant")

        # Act
        await self.assistant_repository.add(assistant)

        # Assert
        assert await self._exists(assistant)

    async def test_save_success(self):
        # Arrange
        assistant = await self._add_assistant()
        assistant.name = "Updated Assistant"

        # Act
        await self.assistant_repository.save(assistant)

        # Assert
        updated_assistant = await self._get(assistant)
        assert updated_assistant
        assert updated_assistant.name == "Updated Assistant"
