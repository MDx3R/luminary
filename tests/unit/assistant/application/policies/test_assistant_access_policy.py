from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.id import UserId
from tests.unit.assistant.utils import make_assistant

from luminary.assistant.application.policies.assistant_access_policy import (
    AssistantAccessPolicy,
)
from luminary.assistant.domain.enums import AssistantType


class TestAssistantAccessPolicy:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.policy = AssistantAccessPolicy()
        self.user_id = UserId(uuid4())

    # personal assistant

    def test_is_allowed_returns_true_for_owner(self):
        # Arrange
        assistant = make_assistant(user_id=self.user_id.value)

        # Act & Assert
        assert self.policy.is_allowed(self.user_id, assistant) is True

    def test_is_allowed_returns_false_for_non_owner(self):
        # Arrange
        assistant = make_assistant()  # different random owner

        # Act & Assert
        assert self.policy.is_allowed(self.user_id, assistant) is False

    def test_assert_is_allowed_passes_for_owner(self):
        # Arrange
        assistant = make_assistant(user_id=self.user_id.value)

        # Act & Assert
        self.policy.assert_is_allowed(self.user_id, assistant)

    def test_assert_is_allowed_raises_for_non_owner(self):
        # Arrange
        assistant = make_assistant()

        # Act & Assert
        with pytest.raises(AccessPolicyError):
            self.policy.assert_is_allowed(self.user_id, assistant)

    # --- system assistant (must always be denied) ---

    def test_is_allowed_returns_false_for_system_assistant_even_as_owner(self):
        # Arrange — system assistant owned by the same user
        assistant = make_assistant(
            type=AssistantType.SYSTEM, user_id=self.user_id.value
        )

        # Act & Assert
        assert self.policy.is_allowed(self.user_id, assistant) is False

    def test_is_allowed_returns_false_for_ownerless_system_assistant(self):
        # Arrange
        assistant = make_assistant(type=AssistantType.SYSTEM, user_id=None)

        # Act & Assert
        assert self.policy.is_allowed(self.user_id, assistant) is False

    def test_assert_is_allowed_raises_for_system_assistant(self):
        # Arrange
        assistant = make_assistant(type=AssistantType.SYSTEM)

        # Act & Assert
        with pytest.raises(
            AccessPolicyError, match="system assistants cannot be modified"
        ):
            self.policy.assert_is_allowed(self.user_id, assistant)

    def test_assert_is_allowed_raises_for_ownerless_system_assistant(self):
        # Arrange
        assistant = make_assistant(type=AssistantType.SYSTEM, user_id=None)

        # Act & Assert
        with pytest.raises(
            AccessPolicyError, match="system assistants cannot be modified"
        ):
            self.policy.assert_is_allowed(self.user_id, assistant)
