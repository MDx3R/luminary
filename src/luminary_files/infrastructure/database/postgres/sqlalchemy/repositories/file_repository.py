from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from luminary_files.application.interfaces.repositories.file_repository import (
    IFileRepository,
)
from luminary_files.domain.entity.file import File
from luminary_files.infrastructure.database.postgres.sqlalchemy.mappers.file_mapper import (
    FileMapper,
)


class FileRepository(IFileRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def add(self, entity: File) -> None:
        model = FileMapper.to_persistence(entity)
        await self.executor.add(model)
