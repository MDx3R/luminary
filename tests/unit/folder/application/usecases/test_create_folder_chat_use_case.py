from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork
from common.domain.value_objects.id import UserId
from tests.unit.chat.utils import make_chat
from tests.unit.folder.utils import make_folder

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.domain.interfaces.chat_factory import ChatFactoryDTO, IChatFactory
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


@pytest.mark.asyncio
class TestCreateFolderChatUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.folder_id = uuid4()
        self.chat_id = uuid4()
        self.model_id = uuid4()

        self.folder = make_folder(
            folder_id=self.folder_id,
            owner_id=self.user_id,
        )
        self.chat = make_chat(
            chat_id=self.chat_id,
            user_id=self.user_id,
            model_id=self.model_id,
        )

        self.folder_repository: AsyncMock = AsyncMock(
            spec=IFolderRepository,
            get_by_id=AsyncMock(return_value=self.folder),
        )
        self.chat_factory: Mock = Mock(
            spec=IChatFactory, create=Mock(return_value=self.chat)
        )
        self.chat_repository: AsyncMock = AsyncMock(spec=IChatRepository)
        self.access_policy: Mock = Mock(spec=IFolderAccessPolicy)

        self.command = CreateFolderChatCommand(
            user_id=self.user_id,
            folder_id=self.folder_id,
            name="New Chat",
            assistant_id=None,
            model_id=self.model_id,
            max_context_messages=10,
        )

        self.use_case = CreateFolderChatUseCase(
            uow=AsyncMock(spec=IUnitOfWork),
            folder_repository=self.folder_repository,
            chat_factory=self.chat_factory,
            chat_repository=self.chat_repository,
            access_policy=self.access_policy,
        )

    async def test_loads_folder_and_checks_access(self) -> None:
        await self.use_case.execute(self.command)

        self.folder_repository.get_by_id.assert_awaited_once()
        self.access_policy.assert_is_allowed.assert_called_once_with(
            UserId(self.user_id), self.folder
        )

    async def test_creates_chat_with_folder_id(self) -> None:
        await self.use_case.execute(self.command)

        self.chat_factory.create.assert_called_once()
        dto = self.chat_factory.create.call_args[0][0]
        assert isinstance(dto, ChatFactoryDTO)
        assert dto.folder_id is not None
        assert dto.folder_id.value == self.folder_id

    async def test_adds_chat_to_repository_and_folder(self) -> None:
        await self.use_case.execute(self.command)

        self.chat_repository.add.assert_awaited_once_with(self.chat)
        assert self.chat.id in self.folder.chats
        self.folder_repository.save.assert_awaited_once_with(self.folder)

    async def test_returns_chat_id(self) -> None:
        result = await self.use_case.execute(self.command)

        assert result == self.chat_id
