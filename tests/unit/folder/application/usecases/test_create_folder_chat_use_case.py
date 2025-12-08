from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork
from common.domain.value_objects.id import UserId
from tests.unit.chat.application.usecases.test_create_chat_use_case import MockModel
from tests.unit.chat.utils import make_chat
from tests.unit.folder.utils import make_folder

from luminary.assistant.domain.entity.assisnant import AssistantId
from luminary.chat.domain.interfaces.chat_factory import IChatFactory
from luminary.chat.infrastructure.database.postgres.sqlalchemy.repositories.chat_repository import (
    ChatRepository,
)
from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.create_folder_chat_use_case import (
    CreateFolderChatCommand,
)
from luminary.folder.application.usecases.command.create_folder_chat_use_case import (
    CreateFolderChatUseCase,
)
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.model.application.interfaces.repositories.model_repository import (
    IModelRepository,
)
from luminary.model.domain.entity.model import ModelId


class TestCreateFolderChatUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = UserId(uuid4())
        self.folder_id = FolderId(uuid4())
        self.assistant_id = AssistantId(uuid4())
        self.model_id = ModelId(uuid4())

        self.chat_factory = Mock(spec=IChatFactory)
        self.folder_access_policy = Mock(spec=IFolderAccessPolicy)  # spec добавлен
        self.folder_repository = AsyncMock(spec=IFolderRepository)
        self.chat_repository = AsyncMock(spec=ChatRepository)
        self.model_repository = Mock(spec=IModelRepository)

        self.uow = AsyncMock(spec=IUnitOfWork)

        self.command = CreateFolderChatCommand(
            user_id=self.user_id.value, folder_id=self.folder_id.value
        )

        self.use_case = CreateFolderChatUseCase(
            uow=self.uow,
            chat_factory=self.chat_factory,
            folder_access_policy=self.folder_access_policy,
            folder_repository=self.folder_repository,
            chat_repository=self.chat_repository,
            model_repository=self.model_repository,
        )

    @pytest.mark.asyncio
    async def test_create_folder_chat_success(self):
        chat = make_chat()

        folder = make_folder(
            folder_id=self.folder_id.value,
            owner_id=self.user_id.value,
            assistant_id=self.assistant_id.value,
        )

        self.folder_repository.get_by_id.return_value = folder
        self.model_repository.get_by_name.return_value = MockModel(
            self.model_id, "gemini-2.5-flash-lite"
        )
        self.chat_factory.create.return_value = chat

        result = await self.use_case.execute(self.command)

        assert result == chat.id.value

        self.folder_access_policy.assert_is_allowed.assert_called_once_with(
            self.user_id, folder
        )
        self.chat_repository.add.assert_awaited_once_with(chat)
