from uuid import UUID

from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import select

from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.domain.entity.source import Source
from luminary.source.infrastructure.database.postgres.sqlalchemy.mappers.source_mapper import (
    SourceMapper,
)
from luminary.source.infrastructure.database.postgres.sqlalchemy.models.source_base import (
    SourceBase,
)


class SourceRepository(ISourceRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, source_id: UUID) -> Source:
        stmt = select(SourceBase).where(SourceBase.source_id == source_id)

        result = await self.executor.execute_scalar_one(stmt)
        if not result:
            raise NotFoundError(source_id)
        return SourceMapper.to_domain(result)

    async def add(self, entity: Source) -> None:
        model = SourceMapper.to_persistence(entity)
        await self.executor.add(model)

    async def save(self, entity: Source) -> None:
        model = SourceMapper.to_persistence(entity)
        await self.executor.save(model)
