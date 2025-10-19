from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError
from tests.unit.assistant.utils import make_assistant

from luminary.assistant.application.policies.assistant_access_policy import (
    AssistantAccessPolicy,
)


@pytest.mark.asyncio
class TestAssistantAccessPolicy:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.assistant_id = uuid4()
        self.user_id = uuid4()
        self.assistant = make_assistant(
            assistant_id=self.assistant_id, user_id=self.user_id
        )
        self.policy = AssistantAccessPolicy()

    async def test_is_allowed_true(self):
        # Act
        result = self.policy.is_allowed(self.user_id, self.assistant)

        # Assert
        assert result is True

    async def test_is_allowed_false(self):
        # Act
        result = self.policy.is_allowed(uuid4(), self.assistant)

        # Assert
        assert result is False

    async def test_create_assistant_no_raise(self):
        # Act & Assert
        self.policy.assert_is_allowed(self.user_id, self.assistant)

    async def test_create_assistant_raises(self):
        # Act & Assert
        with pytest.raises(AccessPolicyError):
            self.policy.assert_is_allowed(uuid4(), self.assistant)
