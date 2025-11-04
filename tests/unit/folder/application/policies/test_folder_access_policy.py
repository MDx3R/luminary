from datetime import UTC, datetime
from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.datetime import DateTime

from luminary.folder.application.policies.folder_access_policy import FolderAccessPolicy
from luminary.folder.domain.entity.folder import Folder, FolderInfo


class TestFolderAccessPolicy:
    @pytest.fixture
    def setup(self):
        self.policy = FolderAccessPolicy()
        self.user_id = uuid4()
        self.folder = Folder(
            folder_id=uuid4(),
            user_id=self.user_id,
            info=FolderInfo("Test", "Description"),
            model_id=uuid4(),
            assistant_id=uuid4(),
            created_at=DateTime(datetime.now(UTC))
        )
        return self

    def test_is_allowed_same_user(self, setup):
        assert setup.policy.is_allowed(setup.user_id, setup.folder) is True

    def test_is_allowed_different_user(self, setup):
        assert setup.policy.is_allowed(uuid4(), setup.folder) is False

    def test_assert_is_allowed_same_user(self, setup):
        # Should not raise
        setup.policy.assert_is_allowed(setup.user_id, setup.folder)

    def test_assert_is_allowed_different_user_raises(self, setup):
        with pytest.raises(AccessPolicyError):
            setup.policy.assert_is_allowed(uuid4(), setup.folder)