from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from luminary.assistant.application.exceptions import AssistantDuplicateNameError
from luminary.assistant.application.interfaces.usecases.command.create_assistant_use_case import (
    ICreateAssistantUseCase,
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

        # Override dependencies
        self.app.dependency_overrides[ICreateAssistantUseCase] = (
            lambda: self.create_assistant_use_case
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
