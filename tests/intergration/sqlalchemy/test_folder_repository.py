from uuid import uuid4
import pytest
from datetime import UTC, datetime

from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from common.domain.value_objects.datetime import DateTime
from luminary.folder.domain.entity.folder import Folder, FolderInfo
from luminary.folder.infrastructure.database.postgres.sqlalchemy.mappers.folder_mapper import FolderMapper
from luminary.folder.infrastructure.database.postgres.sqlalchemy.models.folder_base import FolderBase
from luminary.folder.infrastructure.database.postgres.sqlalchemy.repositories.folder_repository import FolderRepository

@pytest.mark.asyncio
class TestFolderRepository:
    @pytest.fixture(autouse=True)
    def setup(self, maker: async_sessionmaker[AsyncSession], query_executor: QueryExecutor):
        self.maker = maker
        self.folder_repository = FolderRepository(query_executor)

    async def _exists(self, folder: Folder) -> bool:
        async with self.maker() as session:
            result = await session.get(FolderBase, folder.folder_id)
            return result is not None

    async def _get(self, folder: Folder) -> Folder | None:
        async with self.maker() as session:
            result = await session.get(FolderBase, folder.folder_id)
            if not result:
                return None
            return FolderMapper.to_domain(result)

    async def _add_folder(self) -> Folder:
        folder = Folder(
            folder_id=uuid4(),
            user_id=uuid4(),
            info=FolderInfo("Test Folder", "Test Description"),
            model_id=uuid4(),
            assistant_id=uuid4(),
            created_at=DateTime(datetime.now(UTC))
        )
        async with self.maker() as session:
            session.add(FolderMapper.to_persistence(folder))
            await session.commit()
        return folder

    async def test_get_folder_success(self):
        # Arrange
        folder = await self._add_folder()

        # Act
        result = await self.folder_repository.get_by_id(folder.folder_id)

        # Assert
        assert result.folder_id == folder.folder_id

    async def test_get_folder_not_found(self):
        # Act & Assert
        with pytest.raises(NotFoundError):
            await self.folder_repository.get_by_id(uuid4())

    async def test_add_folder_success(self):
        # Arrange
        folder = Folder.create(
            folder_id=uuid4(),
            user_id=uuid4(),
            name="Test Folder",
            description="Test Description",
            model_id=uuid4(),
            assistant_id=uuid4(),
            created_at=DateTime(datetime.now(UTC))
        )
        
        # Act
        await self.folder_repository.add(folder)

        # Assert
        assert await self._exists(folder)

    async def test_save_folder_success(self):
        # Arrange
        folder = await self._add_folder()
        folder.change_name("Updated Name")
        
        # Act
        await self.folder_repository.save(folder)
        
        # Assert
        updated_folder = await self._get(folder)
        # Добавлена проверка на None
        assert updated_folder is not None
        assert updated_folder.info.name == "Updated Name"