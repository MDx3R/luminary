from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.id import UserId
from tests.unit.assistant.utils import make_instructions

from luminary.assistant.domain.entity.assisnant import (
    Assistant,
    AssistantId,
    AssistantInfo,
)


class TestAssistantEntity:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.assistant_id = AssistantId(uuid4())
        self.user_id = UserId(uuid4())
        self.assistant = Assistant(
            id=self.assistant_id,
            owner_id=self.user_id,
            info=AssistantInfo(name="Test Assistant", description="Test Description"),
            instructions=make_instructions(prompt="Test Prompt"),
            is_deleted=False,
        )

    def test_create_assistant_success(self):
        # Arrange
        name = "Test Assistant"
        description = "Test Description"
        instructions = make_instructions(prompt="Test Prompt")

        # Act
        assistant = Assistant.create(
            id=self.assistant_id,
            owner_id=self.user_id,
            name=name,
            description=description,
            instructions=instructions,
        )

        # Assert
        assert assistant.id == self.assistant_id
        assert assistant.owner_id == self.user_id
        assert assistant.info.name == name
        assert assistant.info.description == description
        assert assistant.instructions == instructions
        assert assistant.is_deleted is False

    def test_create_assistant_invalid_name(self):
        # Arrange & Act & Assert
        with pytest.raises(InvariantViolationError):
            Assistant.create(
                id=self.assistant_id,
                owner_id=self.user_id,
                name="",
                description="Test Description",
                instructions=make_instructions(),
            )

    def test_create_assistant_invalid_description(self):
        # Arrange & Act & Assert
        with pytest.raises(InvariantViolationError):
            Assistant.create(
                id=self.assistant_id,
                owner_id=self.user_id,
                name="Test Name",
                description="",
                instructions=make_instructions(),
            )

    def test_change_name(self):
        # Arrange
        new_name = "New Name"

        # Act
        self.assistant.change_name(new_name)

        # Assert
        assert self.assistant.info.name == new_name

    def test_change_description(self):
        # Arrange
        new_description = "New Description"

        # Act
        self.assistant.change_description(new_description)

        # Assert
        assert self.assistant.info.description == new_description

    def test_change_instructions(self):
        # Arrange
        new_instructions = make_instructions(prompt="New Prompt")

        # Act
        self.assistant.change_instructions(new_instructions)

        # Assert
        assert self.assistant.instructions == new_instructions

    def test_delete(self):
        # Act
        self.assistant.delete()

        # Assert
        assert self.assistant.is_deleted is True
