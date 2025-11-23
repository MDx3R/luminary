from common.infrastructure.database.sqlalchemy.executor import QueryExecutor

from luminary.content.application.interfaces.repositories.content_repository import (
    IContentRepository,
)
from luminary.content.domain.entity.content import Content
from luminary.content.infrastructure.database.postgres.sqlalchemy.mappers.content_mapper import (
    ContentMapper,
)


class ContentRepository(IContentRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def add(self, entity: Content) -> None:
        model = ContentMapper.to_persistence(entity)
        await self.executor.add(model)
