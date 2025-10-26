from decimal import Decimal
from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from luminary.model.domain.entity.model import Model
from luminary.model.infrastructure.database.postgres.sqlalchemy.mappers.model_mapper import (
    ModelMapper,
)
from luminary.model.infrastructure.database.postgres.sqlalchemy.models.model_base import (
    ModelBase,
)
from luminary.model.infrastructure.database.postgres.sqlalchemy.repositories.model_repository import (
    ModelRepository,
)


@pytest.mark.asyncio
class TestModelRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self, maker: async_sessionmaker[AsyncSession], query_executor: QueryExecutor
    ):
        self.maker = maker
        self.model_repository = ModelRepository(query_executor)

    async def _exists(self, model: Model) -> bool:
        async with self.maker() as session:
            result = await session.get(ModelBase, model.model_id)
            return result is not None

    async def _get(self, model: Model) -> Model | None:
        async with self.maker() as session:
            result = await session.get(ModelBase, model.model_id)
            if not result:
                return None
            return ModelMapper.to_domain(result)

    async def _add_model(self, name: str = "Test Model") -> Model:
        model = Model.create(
            model_id=uuid4(),
            name=name,
            description="Test Description",
            input_price=Decimal("0.0020"),
            output_price=Decimal("0.0060"),
        )
        async with self.maker() as session:
            session.add(ModelMapper.to_persistence(model))
            await session.commit()
        return model

    async def test_get_model_by_id_success(self):
        # Arrange
        model = await self._add_model()

        # Act
        result = await self.model_repository.get_by_id(model.model_id)

        # Assert
        assert result == model

    async def test_get_model_by_id_not_found(self):
        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.model_repository.get_by_id(uuid4())

    async def test_get_model_by_name_success(self):
        # Arrange
        model = await self._add_model("Gemini 2.0")

        # Act
        result = await self.model_repository.get_by_name("Gemini 2.0")

        # Assert
        assert result == model

    async def test_get_model_by_name_not_found(self):
        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.model_repository.get_by_name("NonExistent")

    async def test_get_all_success(self):
        # Arrange
        expected_min_count = 2
        model1 = await self._add_model("Model 1")
        model2 = await self._add_model("Model 2")

        # Act
        result = await self.model_repository.get_all()

        # Assert
        assert len(result) >= expected_min_count
        assert model1 in result
        assert model2 in result

    async def test_add_success(self):
        # Arrange
        model = Model.create(
            model_id=uuid4(),
            name="New Model",
            description="New Description",
            input_price=Decimal("0.0010"),
            output_price=Decimal("0.0030"),
        )

        # Act
        await self.model_repository.add(model)

        # Assert
        assert await self._exists(model)

    async def test_save_success(self):
        # Arrange
        model = await self._add_model()
        original_name = model.name

        # Act
        model = Model.create(
            model_id=model.model_id,
            name="Updated Model",
            description=model.description,
            input_price=model.input_price,
            output_price=model.output_price,
        )
        await self.model_repository.save(model)

        # Assert
        updated_model = await self._get(model)
        assert updated_model
        assert updated_model.name == "Updated Model"
        assert updated_model.name != original_name
