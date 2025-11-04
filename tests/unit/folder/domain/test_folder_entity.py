from datetime import UTC, datetime
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime

from luminary.folder.domain.entity.folder import Folder, FolderInfo


class TestFolderEntity:
    @pytest.fixture
    def folder_data(self):
        return {
            'folder_id': uuid4(),
            'user_id': uuid4(),
            'name': "Test Folder",
            'description': "Test Description",
            'model_id': uuid4(),
            'assistant_id': uuid4(),
            'created_at': DateTime(datetime.now(UTC))
        }

    def test_create_folder_success(self, folder_data):
        folder = Folder.create(**folder_data)
        
        assert folder.folder_id == folder_data['folder_id']
        assert folder.user_id == folder_data['user_id']
        assert folder.info.name == folder_data['name']
        assert folder.info.description == folder_data['description']
        assert folder.model_id == folder_data['model_id']
        assert folder.assistant_id == folder_data['assistant_id']

    def test_folder_info_empty_name_raises_error(self):
        with pytest.raises(InvariantViolationError):
            FolderInfo(name="", description="Test")

    def test_change_name_success(self, folder_data):
        folder = Folder.create(**folder_data)
        new_name = "Updated Name"
        
        folder.change_name(new_name)
        
        assert folder.info.name == new_name
        assert folder.info.description == folder_data['description']

    def test_change_description_success(self, folder_data):
        folder = Folder.create(**folder_data)
        new_description = "Updated Description"
        
        folder.change_description(new_description)
        
        assert folder.info.description == new_description
        assert folder.info.name == folder_data['name']

    def test_add_and_remove_chat(self, folder_data):
        folder = Folder.create(**folder_data)
        chat_id = uuid4()
        
        folder.add_chat(chat_id)
        assert folder.has_chat(chat_id)
        
        folder.remove_chat(chat_id)
        assert not folder.has_chat(chat_id)

    def test_add_and_remove_source(self, folder_data):
        folder = Folder.create(**folder_data)
        source_id = uuid4()
        
        folder.add_source(source_id)
        assert folder.has_source(source_id)
        
        folder.remove_source(source_id)
        assert not folder.has_source(source_id)

    def test_change_model_and_assistant(self, folder_data):
        folder = Folder.create(**folder_data)
        new_model_id = uuid4()
        new_assistant_id = uuid4()
        
        folder.change_model(new_model_id)
        folder.change_assistant(new_assistant_id)
        
        assert folder.model_id == new_model_id
        assert folder.assistant_id == new_assistant_id