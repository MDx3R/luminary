from common.application.exceptions import NotFoundError
from common.domain.value_objects.object_key import ObjectKey
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from luminary_files.application.interfaces.repositories.file_repository import (
    IFileRepository,
)
from luminary_files.domain.entity.file import File, FileId
from luminary_files.infrastructure.database.postgres.sqlalchemy.mappers.file_mapper import (
    FileMapper,
)
from luminary_files.infrastructure.database.postgres.sqlalchemy.models.file_base import (
    FileBase,
)
from sqlalchemy import select


class FileRepository(IFileRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, id: FileId) -> File:
        stmt = select(FileBase).where(FileBase.file_id == id.value)

        result = await self.executor.execute_scalar_one(stmt)

        if result is None:
            raise NotFoundError(id)

        return FileMapper.to_domain(result)

    async def get_by_object_key(self, key: ObjectKey) -> File:
        stmt = select(FileBase).where(FileBase.object_key == key.value)

        result = await self.executor.execute_scalar_one(stmt)

        if result is None:
            raise NotFoundError(key.value)

        return FileMapper.to_domain(result)

    async def add(self, entity: File) -> None:
        model = FileMapper.to_persistence(entity)
        await self.executor.add(model)
