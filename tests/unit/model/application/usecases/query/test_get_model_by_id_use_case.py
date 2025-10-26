from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from tests.unit.model.utils import make_model

from luminary.model.application.dto.model_dto import ModelDTO
from luminary.model.application.interfaces.repositories.model_repository import (
    IModelRepository,
)
from luminary.model.application.interfaces.usecases.query.get_model_by_id_use_case import (
    GetModelByIdQuery,
)
from luminary.model.application.usecases.query.get_model_by_id_use_case import (
    GetModelByIdUseCase,
)


@pytest.mark.asyncio
class TestGetModelByIdUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.model_id = uuid4()
        self.model = make_model(model_id=self.model_id)

        self.model_repository = AsyncMock(spec=IModelRepository)

        self.query = GetModelByIdQuery(model_id=self.model_id)

        self.use_case = GetModelByIdUseCase(self.model_repository)

    async def test_get_model_by_id_success(self):
        # Arrange
        self.model_repository.get_by_id.return_value = self.model

        # Act
        result = await self.use_case.execute(self.query)

        # Assert
        assert result == ModelDTO.from_entity(self.model)
        self.model_repository.get_by_id.assert_awaited_once_with(self.model_id)

    async def test_get_model_by_id_not_found(self):
        # Arrange
        self.model_repository.get_by_id.side_effect = NotFoundError(self.model_id)

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await self.use_case.execute(self.query)

        assert exc_info.value.entity_id == self.model_id
        self.model_repository.get_by_id.assert_awaited_once_with(self.model_id)
