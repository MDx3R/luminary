"""Read repository implementation for Source: ORM -> read models."""

from collections.abc import Sequence
from uuid import UUID

from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import select
from sqlalchemy.orm import with_polymorphic

from luminary.source.application.dtos.read_models import SourceReadModel
from luminary.source.application.interfaces.repositories.source_read_repository import (
    ISourceReadRepository,
)
from luminary.source.infrastructure.database.postgres.sqlalchemy.mappers.source_mapper import (
    SourceReadMapper,
)
from luminary.source.infrastructure.database.postgres.sqlalchemy.models.source_base import (
    SourceBase,
)


class SourceReadRepository(ISourceReadRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self._executor = executor

    async def get_by_id(self, source_id: UUID, owner_id: UUID) -> SourceReadModel:
        poly = with_polymorphic(SourceBase, "*")
        stmt = (
            select(poly)
            .where(poly.source_id == source_id)
            .where(poly.owner_id == owner_id)
            .where(poly.is_active)
        )
        row = await self._executor.execute_scalar_one(stmt)
        if not row:
            raise NotFoundError(str(source_id))
        return SourceReadMapper.to_read(row)

    async def list_by_owner(self, owner_id: UUID) -> Sequence[SourceReadModel]:
        poly = with_polymorphic(SourceBase, "*")
        stmt = (
            select(poly)
            .where(poly.owner_id == owner_id)
            .where(poly.is_active)
            .order_by(poly.created_at.desc())
        )
        rows = await self._executor.execute_scalar_many(stmt)
        return [SourceReadMapper.to_read(r) for r in rows]
