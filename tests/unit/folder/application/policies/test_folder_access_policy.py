from uuid import uuid4

import pytest
from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.id import UserId
from tests.unit.folder.utils import make_folder

from luminary.folder.application.policies.folder_access_policy import FolderAccessPolicy


class TestFolderAccessPolicy:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.policy = FolderAccessPolicy()
        self.folder = make_folder()
        self.user_id = self.folder.owner_id

    def test_is_allowed_same_user(self):
        assert self.policy.is_allowed(self.user_id, self.folder) is True

    def test_is_allowed_different_user(self):
        assert self.policy.is_allowed(UserId(uuid4()), self.folder) is False

    def test_assert_is_allowed_same_user(self):
        # Should not raise
        self.policy.assert_is_allowed(self.user_id, self.folder)

    def test_assert_is_allowed_different_user_raises(self):
        with pytest.raises(AccessPolicyError):
            self.policy.assert_is_allowed(UserId(uuid4()), self.folder)
