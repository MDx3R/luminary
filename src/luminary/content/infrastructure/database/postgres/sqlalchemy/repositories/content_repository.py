from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import select

from luminary.content.application.interfaces.repositories.content_repository import (
    IContentRepository,
)
from luminary.content.domain.entity.content import Content, ContentId
from luminary.content.infrastructure.database.postgres.sqlalchemy.mappers.content_mapper import (
    ContentMapper,
)
from luminary.content.infrastructure.database.postgres.sqlalchemy.models.content_base import (
    ContentBase,
)


class ContentRepository(IContentRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, id: ContentId) -> Content:
        stmt = select(ContentBase).where(ContentBase.content_id == id.value)

        result = await self.executor.execute_scalar_one(stmt)

        if result is None:
            raise NotFoundError(id)

        return ContentMapper.to_domain(result)

    async def add(self, entity: Content) -> None:
        model = ContentMapper.to_persistence(entity)
        await self.executor.add(model)
