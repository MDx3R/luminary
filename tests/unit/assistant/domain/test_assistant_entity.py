from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.id import UserId
from tests.unit.assistant.utils import make_assistant, make_instructions

from luminary.assistant.domain.entity.assistant import (
    MAX_TAG_LENGTH,
    MAX_TAGS_COUNT,
    Assistant,
    AssistantId,
    AssistantInfo,
)
from luminary.assistant.domain.enums import AssistantType
from luminary.assistant.domain.events.events import (
    AssistantClonedEvent,
    AssistantCreatedEvent,
    AssistantPublishedEvent,
)


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
            tags=[],
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

    # --- tags ---

    def test_tags_default_to_empty_list(self):
        assert self.assistant.tags == []

    def test_create_assistant_with_tags(self):
        # Arrange & Act
        assistant = Assistant.create(
            id=self.assistant_id,
            owner_id=self.user_id,
            type=AssistantType.PERSONAL,
            name="Test",
            description="Desc",
            instructions=make_instructions(),
            tags=["python", "qa"],
        )

        # Assert
        assert assistant.tags == ["python", "qa"]

    def test_change_tags_replaces_list(self):
        # Arrange
        self.assistant.change_tags(["a", "b"])

        # Assert
        assert self.assistant.tags == ["a", "b"]

    def test_change_tags_to_empty_clears_list(self):
        # Arrange
        self.assistant.change_tags(["a"])

        # Act
        self.assistant.change_tags([])

        # Assert
        assert self.assistant.tags == []

    def test_change_tags_raises_when_tag_exceeds_max_length(self):
        # Arrange
        long_tag = "x" * (MAX_TAG_LENGTH + 1)

        # Act & Assert
        with pytest.raises(InvariantViolationError, match="cannot exceed"):
            self.assistant.change_tags([long_tag])

    def test_change_tags_raises_when_too_many_tags(self):
        # Arrange
        too_many = ["tag"] * (MAX_TAGS_COUNT + 1)

        # Act & Assert
        with pytest.raises(InvariantViolationError, match="more than"):
            self.assistant.change_tags(too_many)

    def test_change_tags_raises_when_empty_tag_string(self):
        # Act & Assert
        with pytest.raises(InvariantViolationError, match="empty"):
            self.assistant.change_tags(["valid", ""])

    def test_create_raises_when_tags_invalid(self):
        # Arrange & Act & Assert
        with pytest.raises(InvariantViolationError):
            Assistant.create(
                id=self.assistant_id,
                owner_id=self.user_id,
                type=AssistantType.PERSONAL,
                name="Test",
                description="Desc",
                instructions=make_instructions(),
                tags=["x" * (MAX_TAG_LENGTH + 1)],
            )

    def test_tags_matches_returns_true_when_equal(self):
        # Arrange
        self.assistant.change_tags(["a", "b"])

        # Assert
        assert self.assistant.tags_matches(["a", "b"]) is True

    def test_tags_matches_returns_false_when_different(self):
        # Arrange
        self.assistant.change_tags(["a"])

        # Assert
        assert self.assistant.tags_matches(["b"]) is False

    # --- owner_id optional for system assistants ---

    def test_system_assistant_can_have_no_owner(self):
        # Act
        assistant = make_assistant(type=AssistantType.SYSTEM, user_id=None)

        # Assert
        assert assistant.owner_id is None
        assert assistant.type == AssistantType.SYSTEM

    def test_non_system_assistant_requires_owner(self):
        # Act & Assert
        with pytest.raises(InvariantViolationError, match="Only system assistants"):
            Assistant(
                id=self.assistant_id,
                owner_id=None,
                type=AssistantType.PERSONAL,
                info=AssistantInfo(name="Test", description="Desc"),
                instructions=make_instructions(),
                is_deleted=False,
            )

    def test_system_assistant_without_owner_is_not_owned_by_any_user(self):
        # Arrange
        system_assistant = make_assistant(type=AssistantType.SYSTEM, user_id=None)

        # Assert
        assert system_assistant.is_owned_by(self.user_id) is False

    # --- publish ---

    def test_publish_changes_type_to_public(self):
        # Act
        self.assistant.publish()

        # Assert
        assert self.assistant.type == AssistantType.PUBLIC

    def test_publish_emits_published_event(self):
        # Act
        self.assistant.publish()

        # Assert
        assert len(self.assistant.events) == 1
        assert isinstance(self.assistant.events[0], AssistantPublishedEvent)

    def test_publish_raises_for_system_assistant(self):
        # Arrange
        system_assistant = make_assistant(type=AssistantType.SYSTEM)

        # Act & Assert
        with pytest.raises(InvariantViolationError, match="Only personal assistants"):
            system_assistant.publish()

    def test_publish_raises_for_already_public_assistant(self):
        # Arrange
        public_assistant = make_assistant(type=AssistantType.PUBLIC)

        # Act & Assert
        with pytest.raises(InvariantViolationError, match="Only personal assistants"):
            public_assistant.publish()

    # --- clone ---

    def test_clone_creates_personal_assistant_with_new_id(self):
        # Arrange
        new_id = AssistantId(uuid4())
        new_owner = UserId(uuid4())

        # Act
        clone = Assistant.clone(
            source=self.assistant, new_id=new_id, new_owner_id=new_owner
        )

        # Assert
        assert clone.id == new_id
        assert clone.owner_id == new_owner
        assert clone.type == AssistantType.PERSONAL

    def test_clone_copies_info_instructions_and_tags(self):
        # Arrange
        self.assistant.change_tags(["a", "b"])
        new_id = AssistantId(uuid4())
        new_owner = UserId(uuid4())

        # Act
        clone = Assistant.clone(
            source=self.assistant, new_id=new_id, new_owner_id=new_owner
        )

        # Assert
        assert clone.info == self.assistant.info
        assert clone.instructions == self.assistant.instructions
        assert clone.tags == ["a", "b"]

    def test_clone_tags_are_independent_copy(self):
        # Arrange
        self.assistant.change_tags(["x"])
        new_id = AssistantId(uuid4())
        clone = Assistant.clone(
            source=self.assistant, new_id=new_id, new_owner_id=UserId(uuid4())
        )

        # Act — mutate original tags
        self.assistant.change_tags(["y"])

        # Assert — clone is unaffected
        assert clone.tags == ["x"]

    def test_clone_emits_cloned_event(self):
        # Arrange
        new_id = AssistantId(uuid4())

        # Act
        clone = Assistant.clone(
            source=self.assistant, new_id=new_id, new_owner_id=UserId(uuid4())
        )

        # Assert
        assert len(clone.events) == 1
        event = clone.events[0]
        assert isinstance(event, AssistantClonedEvent)
        assert event.assistant_id == new_id.value
        assert event.source_assistant_id == self.assistant.id.value

    def test_clone_is_not_deleted(self):
        # Arrange — deleted source
        self.assistant.delete()
        new_id = AssistantId(uuid4())

        # Act
        clone = Assistant.clone(
            source=self.assistant, new_id=new_id, new_owner_id=UserId(uuid4())
        )

        # Assert
        assert clone.is_deleted is False
