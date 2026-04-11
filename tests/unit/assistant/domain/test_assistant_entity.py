from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.id import UserId
from tests.unit.assistant.utils import make_assistant, make_instructions

from luminary.assistant.domain.entity.assistant import (
    Assistant,
    AssistantId,
    AssistantInfo,
)
from luminary.assistant.domain.enums import AssistantType
from luminary.assistant.domain.events.events import AssistantCreatedEvent


class TestAssistantEntity:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.assistant_id = AssistantId(uuid4())
        self.user_id = UserId(uuid4())
        self.assistant = Assistant(
            id=self.assistant_id,
            owner_id=self.user_id,
            type=AssistantType.PERSONAL,
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
            type=AssistantType.PERSONAL,
            name=name,
            description=description,
            instructions=instructions,
        )

        # Assert
        assert assistant.id == self.assistant_id
        assert assistant.owner_id == self.user_id
        assert assistant.type == AssistantType.PERSONAL
        assert assistant.info.name == name
        assert assistant.info.description == description
        assert assistant.instructions == instructions
        assert assistant.is_deleted is False
        assert len(assistant.events) == 1

    def test_create_assistant_emits_created_event(self):
        assistant = Assistant.create(
            id=self.assistant_id,
            owner_id=self.user_id,
            type=AssistantType.PERSONAL,
            name="Test",
            description="Desc",
            instructions=make_instructions(),
        )
        assert assistant.has_changes()
        assert len(assistant.events) == 1

        event = assistant.events[0]
        assert isinstance(event, AssistantCreatedEvent)
        assert event.assistant_id == self.assistant_id.value

    def test_create_assistant_invalid_name(self):
        # Arrange & Act & Assert
        with pytest.raises(InvariantViolationError):
            Assistant.create(
                id=self.assistant_id,
                owner_id=self.user_id,
                type=AssistantType.PERSONAL,
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
                type=AssistantType.PERSONAL,
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
        assert len(self.assistant.events) == 1

    def test_change_description(self):
        # Arrange
        new_description = "New Description"

        # Act
        self.assistant.change_description(new_description)

        # Assert
        assert self.assistant.info.description == new_description
        assert len(self.assistant.events) == 1

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
        assert len(self.assistant.events) == 1

    def test_delete_system_assistant_raises(self):
        system_assistant = make_assistant(type=AssistantType.SYSTEM)

        with pytest.raises(
            InvariantViolationError, match="System assistant cannot be deleted"
        ):
            system_assistant.delete()

    def test_delete_idempotent_when_already_deleted(self):
        self.assistant.delete()
        assert len(self.assistant.events) == 1
        self.assistant.delete()
        assert self.assistant.is_deleted is True
        assert len(self.assistant.events) == 1
