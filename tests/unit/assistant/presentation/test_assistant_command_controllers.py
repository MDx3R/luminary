from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from luminary.assistant.application.exceptions import AssistantDuplicateNameError
from luminary.assistant.application.interfaces.usecases.command.create_assistant_use_case import (
    ICreateAssistantUseCase,
)
from luminary.assistant.application.interfaces.usecases.command.delete_assistant_use_case import (
    IDeleteAssistantUseCase,
)
from luminary.assistant.application.interfaces.usecases.command.update_assistant_use_case import (
    IUpdateAssistantUseCase,
)
from luminary.assistant.presentation.http.fastapi.controllers import (
    assistant_command_router,
)


@pytest.mark.asyncio
class TestAssistantControllers:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = FastAPI()
        self.app.include_router(assistant_command_router)
        self.client: TestClient = TestClient(self.app)

        # Mock UseCases
        self.create_assistant_use_case = AsyncMock(spec=ICreateAssistantUseCase)
        self.update_assistant_use_case = AsyncMock(spec=IUpdateAssistantUseCase)
        self.delete_assistant_use_case = AsyncMock(spec=IDeleteAssistantUseCase)

        # Override dependencies
        self.app.dependency_overrides[ICreateAssistantUseCase] = (
            lambda: self.create_assistant_use_case
        )
        self.app.dependency_overrides[IUpdateAssistantUseCase] = (
            lambda: self.update_assistant_use_case
        )
        self.app.dependency_overrides[IDeleteAssistantUseCase] = (
            lambda: self.delete_assistant_use_case
        )

    async def test_create_assistant_success(self):
        # Arrange
        name = "Test Assistant"
        description = "Test Description"
        prompt = "Test Prompt"
        assistant_id = uuid4()
        self.create_assistant_use_case.execute.return_value = assistant_id

        # Act
        response = self.client.post(
            "/",
            json={"name": name, "description": description, "prompt": prompt},
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer valid_token",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"id": str(assistant_id)}
        self.create_assistant_use_case.execute.assert_awaited_once()

    async def test_create_assistant_duplicate_name(self):
        # Arrange
        name = "Duplicate Assistant"
        description = "Test Description"
        prompt = "Test Prompt"
        self.create_assistant_use_case.execute.side_effect = (
            AssistantDuplicateNameError(uuid4(), name)
        )

        # Act
        response = self.client.post(
            "/",
            json={"name": name, "description": description, "prompt": prompt},
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer valid_token",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"]["error"] == "AssistantDuplicateNameError"

    async def test_create_assistant_unauthenticated(self):
        # Act
        response = self.client.post(
            "/",
            json={"name": "Test", "description": "Desc", "prompt": "Prompt"},
            headers={"Content-Type": "application/json"},
        )

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        self.create_assistant_use_case.execute.assert_not_awaited()

    async def test_update_assistant_success(self):
        # Arrange
        assistant_id = uuid4()
        name = "Updated"
        description = "Desc"
        prompt = None
        self.update_assistant_use_case.execute.return_value = None

        # Act
        response = self.client.patch(
            f"/{assistant_id}",
            json={"name": name, "description": description, "prompt": prompt},
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer valid_token",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        self.update_assistant_use_case.execute.assert_awaited_once()

    async def test_update_assistant_not_found(self):
        # Arrange
        assistant_id = uuid4()

        self.update_assistant_use_case.execute.side_effect = NotFoundError(assistant_id)

        # Act
        response = self.client.patch(
            f"/{assistant_id}",
            json={"name": "n", "description": "d", "prompt": None},
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer valid_token",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_assistant_success(self):
        # Arrange
        assistant_id = uuid4()
        self.delete_assistant_use_case.execute.return_value = None

        # Act
        response = self.client.delete(
            f"/{assistant_id}",
            headers={
                "Authorization": "Bearer valid_token",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        self.delete_assistant_use_case.execute.assert_awaited_once()

    async def test_delete_assistant_ignores_not_found(self):
        # Arrange
        assistant_id = uuid4()
        self.delete_assistant_use_case.execute.side_effect = NotFoundError(assistant_id)

        # Act
        response = self.client.delete(
            f"/{assistant_id}",
            headers={
                "Authorization": "Bearer valid_token",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        self.delete_assistant_use_case.execute.assert_awaited_once()

    async def test_delete_assistant_unauthenticated(self):
        # Arrange
        assistant_id = uuid4()

        # Act
        response = self.client.delete(f"/{assistant_id}")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        self.delete_assistant_use_case.execute.assert_not_awaited()
