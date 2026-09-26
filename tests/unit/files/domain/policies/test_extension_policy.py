import pytest
from luminary_files.domain.policies.extenstion_policy import MIMEWhitelistPolicy


class TestMIMEWhitelistPolicy:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.ext = ["ext", "ext2", "ext3"]
        self.ext_policy = MIMEWhitelistPolicy(self.ext)

    def test_is_allowed_true(self):
        for i in self.ext:
            assert self.ext_policy.is_allowed(i) is True

    def test_is_allowed_false(self):
        assert self.ext_policy.is_allowed("some-ext") is False
