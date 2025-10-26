from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from luminary.model.application.dto.model_dto import ModelDTO
from luminary.model.application.interfaces.usecases.query.get_all_models_use_case import (
    IGetAllModelsUseCase,
)
from luminary.model.application.interfaces.usecases.query.get_model_by_id_use_case import (
    IGetModelByIdUseCase,
)
from luminary.model.presentation.http.fastapi.controllers import model_query_router


@pytest.mark.asyncio
class TestModelQueryControllers:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = FastAPI()
        self.app.include_router(model_query_router)
        self.client: TestClient = TestClient(self.app)

        # Mock UseCases
        self.get_model_by_id_use_case = AsyncMock(spec=IGetModelByIdUseCase)
        self.get_all_models_use_case = AsyncMock(spec=IGetAllModelsUseCase)

        # Override dependencies
        self.app.dependency_overrides[IGetModelByIdUseCase] = (
            lambda: self.get_model_by_id_use_case
        )
        self.app.dependency_overrides[IGetAllModelsUseCase] = (
            lambda: self.get_all_models_use_case
        )

    async def test_get_model_by_id_success(self):
        # Arrange
        model_id = uuid4()
        model_dto = ModelDTO(
            model_id=model_id,
            name="Test Model",
            description="Test Description",
            input_price=Decimal("0.0020"),
            output_price=Decimal("0.0060"),
        )
        self.get_model_by_id_use_case.execute.return_value = model_dto

        # Act
        response = self.client.get(
            f"/{model_id}",
            headers={"Authorization": "Bearer valid_token"},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["model_id"] == str(model_id)
        assert data["name"] == "Test Model"
        assert data["description"] == "Test Description"
        self.get_model_by_id_use_case.execute.assert_awaited_once()

    async def test_get_model_by_id_not_found(self):
        # Arrange
        model_id = uuid4()
        self.get_model_by_id_use_case.execute.side_effect = NotFoundError(model_id)

        # Act
        response = self.client.get(
            f"/{model_id}",
            headers={"Authorization": "Bearer valid_token"},
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"]["error"] == "ModelNotFoundError"

    async def test_get_model_by_id_unauthenticated(self):
        # Arrange
        model_id = uuid4()

        # Act
        response = self.client.get(f"/{model_id}")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        self.get_model_by_id_use_case.execute.assert_not_awaited()

    async def test_get_all_models_success(self):
        # Arrange
        expected_count = 2
        model1_dto = ModelDTO(
            model_id=uuid4(),
            name="Model 1",
            description="Description 1",
            input_price=Decimal("0.0020"),
            output_price=Decimal("0.0060"),
        )
        model2_dto = ModelDTO(
            model_id=uuid4(),
            name="Model 2",
            description="Description 2",
            input_price=Decimal("0.0030"),
            output_price=Decimal("0.0090"),
        )
        self.get_all_models_use_case.execute.return_value = [model1_dto, model2_dto]

        # Act
        response = self.client.get(
            "/",
            headers={"Authorization": "Bearer valid_token"},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == expected_count
        assert data[0]["name"] == "Model 1"
        assert data[1]["name"] == "Model 2"
        self.get_all_models_use_case.execute.assert_awaited_once()

    async def test_get_all_models_empty(self):
        # Arrange
        self.get_all_models_use_case.execute.return_value = []

        # Act
        response = self.client.get(
            "/",
            headers={"Authorization": "Bearer valid_token"},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
        self.get_all_models_use_case.execute.assert_awaited_once()

    async def test_get_all_models_unauthenticated(self):
        # Act
        response = self.client.get("/")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        self.get_all_models_use_case.execute.assert_not_awaited()
