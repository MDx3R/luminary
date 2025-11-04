from unittest.mock import Mock
from uuid import uuid4
import pytest

from luminary.folder.domain.factories.folder_factory import FolderFactory
from luminary.folder.domain.entity.folder import Folder

class TestFolderFactory:
    @pytest.fixture
    def factory(self):
        clock = Mock()
        clock.now.return_value = Mock()
        uuid_generator = Mock()
        uuid_generator.create.return_value = uuid4()
        
        return FolderFactory(clock, uuid_generator)

    def test_create_folder_success(self, factory):
        name = "Test Folder"
        description = "Test Description"
        user_id = uuid4()
        model_id = uuid4()
        assistant_id = uuid4()
        
        folder = factory.create(name, description, user_id, model_id, assistant_id)
        
        assert isinstance(folder, Folder)
        assert folder.info.name == name
        assert folder.info.description == description
        assert folder.user_id == user_id
        assert folder.model_id == model_id
        assert folder.assistant_id == assistant_id

    def test_create_folder_with_none_description(self, factory):
        folder = factory.create("Test", None, uuid4(), uuid4(), uuid4())
        
        assert folder.info.description is None