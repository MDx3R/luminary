from unittest.mock import AsyncMock, Mock
from uuid import uuid4
import pytest

from luminary.folder.application.usecases.command.create_folder_chat_use_case import CreateFolderChatUseCase
from luminary.folder.application.interfaces.usecases.command.create_folder_chat_use_case import CreateFolderChatCommand

class TestCreateFolderChatUseCase:
    @pytest.fixture
    def setup(self):
        self.chat_factory = Mock()
        self.folder_access_policy = Mock()
        self.assistant_service = Mock()
        self.assistant_repository = AsyncMock()
        self.folder_repository = AsyncMock()
        self.chat_repository = AsyncMock()
        
        self.use_case = CreateFolderChatUseCase(
            self.chat_factory,
            self.folder_access_policy,
            self.assistant_service,
            self.assistant_repository,
            self.folder_repository,
            self.chat_repository
        )
        
        self.command = CreateFolderChatCommand(
            user_id=uuid4(),
            folder_id=uuid4()
        )
        
        return self

    @pytest.mark.asyncio
    async def test_create_folder_chat_success(self, setup):
        folder = Mock()
        folder.folder_id = setup.command.folder_id
        folder.assistant_id = uuid4()
        folder.model_id = uuid4()
        
        assistant = Mock()
        assistant.instructions.prompt = "Test prompt"
        
        chat = Mock()
        chat.chat_id = uuid4()
        
        setup.folder_repository.get_by_id.return_value = folder
        setup.assistant_repository.get_by_id.return_value = assistant
        setup.chat_factory.create.return_value = chat
        
        result = await setup.use_case.execute(setup.command)
        
        assert result == chat.chat_id
        setup.folder_access_policy.assert_is_allowed.assert_called_once_with(
            setup.command.user_id, folder
        )
        setup.chat_repository.add.assert_awaited_once_with(chat)