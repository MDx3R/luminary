from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import joinedload
from tests.unit.folder.utils import make_folder

from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.domain.entity.folder import Folder, FolderId
from luminary.folder.infrastructure.database.postgres.sqlalchemy.mappers.folder_mapper import (
    FolderMapper,
)
from luminary.folder.infrastructure.database.postgres.sqlalchemy.models.folder_base import (
    FolderBase,
)
from luminary.folder.infrastructure.database.postgres.sqlalchemy.repositories.folder_repository import (
    FolderRepository,
)
from luminary.source.domain.entity.source import SourceId


@pytest.mark.asyncio
class TestFolderRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self, maker: async_sessionmaker[AsyncSession], query_executor: QueryExecutor
    ):
        self.maker = maker
        self.folder_repository = FolderRepository(query_executor)

    async def _exists(self, folder_id: FolderId) -> bool:
        async with self.maker() as session:
            return await session.get(FolderBase, folder_id.value) is not None

    async def _get_folder(self, folder_id: FolderId) -> Folder | None:
        async with self.maker() as session:
            result = (
                (
                    await session.execute(
                        select(FolderBase)
                        .where(FolderBase.folder_id == folder_id.value)
                        .options(joinedload(FolderBase.chats))
                        .options(joinedload(FolderBase.sources))
                    )
                )
                .unique()
                .scalar_one_or_none()
            )
            if not result:
                return None
            folder = FolderMapper.to_domain(result)
            assert isinstance(folder, Folder)
            return folder

    async def _add_folder(self) -> Folder:
        folder = make_folder()
        async with self.maker() as session:
            session.add(FolderMapper.to_persistence(folder))
            await session.commit()
        return folder

    async def test_get_folder_success(self):
        folder = await self._add_folder()

        # Act
        result = await self.folder_repository.get_by_id(folder.id)

        # Assert
        assert result == folder

    async def test_get_folder_not_found(self):
        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.folder_repository.get_by_id(FolderId(uuid4()))

    async def test_save_folder_success(self):
        # Arrange
        folder = await self._add_folder()
        folder.change_name("New Folder Description")
        folder.change_description("New Folder Description")

        # Act
        await self.folder_repository.save(folder)

        # Assert
        updated_folder = await self._get_folder(folder.id)
        assert updated_folder is not None
        assert updated_folder.info == folder.info

    async def test_add_chat_success(self):
        # Arrange
        folder = await self._add_folder()
        chat_id = ChatId(uuid4())
        folder.add_chat(chat_id)

        # Act
        await self.folder_repository.save(folder)

        # Assert
        updated_folder = await self._get_folder(folder.id)
        assert updated_folder is not None
        assert updated_folder.chats == folder.chats

    async def test_add_source_success(self):
        # Arrange
        folder = await self._add_folder()
        source_id = SourceId(uuid4())
        folder.add_source(source_id)
        # Act
        await self.folder_repository.save(folder)

        # Assert
        updated_folder = await self._get_folder(folder.id)
        assert updated_folder is not None
        assert updated_folder.sources == folder.sources

    async def test_remove_folder_success(self):
        # TODO: remove not yet supported
        pass
