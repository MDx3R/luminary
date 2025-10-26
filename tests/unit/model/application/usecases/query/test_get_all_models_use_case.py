from unittest.mock import AsyncMock

import pytest
from tests.unit.model.utils import make_model

from luminary.model.application.dto.model_dto import ModelDTO
from luminary.model.application.interfaces.repositories.model_repository import (
    IModelRepository,
)
from luminary.model.application.usecases.query.get_all_models_use_case import (
    GetAllModelsUseCase,
)


@pytest.mark.asyncio
class TestGetAllModelsUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.model_repository = AsyncMock(spec=IModelRepository)

        self.use_case = GetAllModelsUseCase(self.model_repository)

    async def test_get_all_models_success(self):
        # Arrange
        expected_count = 2
        model1 = make_model(name="Model 1")
        model2 = make_model(name="Model 2")
        self.model_repository.get_all.return_value = [model1, model2]

        # Act
        result = await self.use_case.execute()

        # Assert
        assert len(result) == expected_count
        assert result[0] == ModelDTO.from_entity(model1)
        assert result[1] == ModelDTO.from_entity(model2)
        self.model_repository.get_all.assert_awaited_once()

    async def test_get_all_models_empty(self):
        # Arrange
        self.model_repository.get_all.return_value = []

        # Act
        result = await self.use_case.execute()

        # Assert
        assert result == []
        self.model_repository.get_all.assert_awaited_once()
