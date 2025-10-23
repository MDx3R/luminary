from unittest.mock import AsyncMock, Mock
from uuid import uuid4
import pytest

from tests.unit.chat.utils import make_chat
from src.luminary.chat.application.interfaces.repositories.chat_repository import IChatRepository
from src.luminary.chat.application.interfaces.usecases.command.create_chat_use_case import CreateChatCommand
from src.luminary.chat.application.usecases.command.create_chat_use_case import CreateChatUseCase
from src.luminary.chat.domain.entity.chat import ChatSettings
from src.luminary.chat.domain.interfaces.chat_factory import IChatFactory
from src.luminary.model.application.interfaces.repositories.model_repository import IModelRepository

class MockModel:
    def __init__(self, model_id, name):
        self.model_id = model_id
        self.name = name

@pytest.mark.asyncio
class TestCreateChatUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.chat_id = uuid4()
        self.user_id = uuid4()
        self.model_id = uuid4()
        self.folder_id = uuid4()

        self.chat = make_chat(
            chat_id=self.chat_id,
            user_id=self.user_id,
            model_id=self.model_id,
            folder_id=self.folder_id
        )

        self.chat_repository = AsyncMock(spec=IChatRepository)
        self.chat_factory = Mock(spec=IChatFactory)
        self.model_repository = AsyncMock(spec=IModelRepository)
        self.chat_factory.create.return_value = self.chat
        self.model_repository.get_by_name.return_value = MockModel(
            self.model_id, "gemini-2.5-flash-lite"
        )
        self.command = CreateChatCommand(user_id=self.user_id)
        self.use_case = CreateChatUseCase(
            self.chat_factory, self.chat_repository, self.model_repository
        )

    async def test_create_chat_success(self):
        result = await self.use_case.execute(self.command)
        assert result == self.chat_id
        self.model_repository.get_by_name.assert_awaited_once_with(
            "gemini-2.5-flash-lite"
        )
        self.chat_factory.create.assert_called_once()
        self.chat_repository.add.assert_awaited_once_with(self.chat)

    async def test_create_chat_calls_factory_with_correct_params(self):
        await self.use_case.execute(self.command)
        call_kwargs = self.chat_factory.create.call_args[1]
        assert call_kwargs["user_id"] == self.user_id
        assert call_kwargs["folder_id"] is None
        assert call_kwargs["name"] is None
        
        settings = call_kwargs["settings"]
        assert settings.model_id == self.model_id
        assert settings.system_prompt == "You are a helpful assistant"
        assert settings.max_context_messages == 20
