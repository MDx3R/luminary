from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from tests.unit.assistant.utils import make_instructions

from luminary.assistant.domain.entity.assisnant import Assistant


class TestAssistantEntity:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.assistant_id = uuid4()
        self.user_id = uuid4()
        self.assistant = Assistant(
            assistant_id=self.assistant_id,
            user_id=self.user_id,
            name="Test Assistant",
            description="Test Description",
            instructions=make_instructions(prompt="Test Prompt"),
        )

    def test_create_assistant_success(self):
        # Arrange
        assistant_id = uuid4()
        user_id = uuid4()
        name = "Test Assistant"
        description = "Test Description"
        instructions = make_instructions(prompt="Test Prompt")

        # Act
        assistant = Assistant.create(
            assistant_id=assistant_id,
            user_id=user_id,
            name=name,
            description=description,
            instructions=instructions,
        )

        # Assert
        assert assistant.assistant_id == assistant_id
        assert assistant.user_id == user_id
        assert assistant.name == name
        assert assistant.description == description
        assert assistant.instructions == instructions

    def test_create_assistant_no_instructions(self):
        # Arrange
        assistant_id = uuid4()
        user_id = uuid4()
        name = "Test Assistant"
        description = "Test Description"

        # Act
        assistant = Assistant.create(
            assistant_id=assistant_id,
            user_id=user_id,
            name=name,
            description=description,
            instructions=None,
        )

        # Assert
        assert assistant.instructions is None

    def test_create_assistant_invalid_name(self):
        # Arrange & Act & Assert
        with pytest.raises(InvariantViolationError):
            Assistant.create(
                assistant_id=uuid4(),
                user_id=uuid4(),
                name="",
                description="Test Description",
                instructions=None,
            )

    def test_create_assistant_invalid_description(self):
        # Arrange & Act & Assert
        with pytest.raises(InvariantViolationError):
            Assistant.create(
                assistant_id=uuid4(),
                user_id=uuid4(),
                name="Test Name",
                description="",
                instructions=None,
            )

    def test_change_name(self):
        # Arrange
        new_name = "New Name"

        # Act
        self.assistant.change_name(new_name)

        # Assert
        assert self.assistant.name == new_name

    def test_change_description(self):
        # Arrange
        new_description = "New Description"

        # Act
        self.assistant.change_description(new_description)

        # Assert
        assert self.assistant.description == new_description

    def test_change_instructions(self):
        # Arrange
        new_instructions = make_instructions(prompt="New Prompt")

        # Act
        self.assistant.change_instructions(new_instructions)

        # Assert
        assert self.assistant.instructions == new_instructions

    def test_remove_instructions(self):
        # Act
        self.assistant.remove_instructions()

        # Assert
        assert self.assistant.instructions is None
