"""Read repository implementation for Folder: ORM -> read models (cross-BC)."""

from collections.abc import Sequence
from uuid import UUID

from common.application.exceptions import NotFoundError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import select
from sqlalchemy.orm import joinedload, with_polymorphic

from luminary.assistant.infrastructure.database.postgres.sqlalchemy.models.assistant_base import (
    AssistantBase,
)
from luminary.folder.application.dtos.read_models import (
    FolderReadModel,
    FolderSummaryReadModel,
)
from luminary.folder.application.interfaces.repositories.folder_read_repository import (
    IFolderReadRepository,
)
from luminary.folder.infrastructure.database.postgres.sqlalchemy.mappers.folder_mapper import (
    FolderReadMapper,
)
from luminary.folder.infrastructure.database.postgres.sqlalchemy.models.folder_base import (
    FolderBase,
)
from luminary.source.infrastructure.database.postgres.sqlalchemy.models.source_base import (
    SourceBase,
)


class FolderReadRepository(IFolderReadRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self._executor = executor

    async def get_by_id(self, folder_id: UUID, owner_id: UUID) -> FolderReadModel:
        sources = with_polymorphic(SourceBase, "*", aliased=True)
        stmt = (
            select(FolderBase)
            .where(FolderBase.folder_id == folder_id)
            .where(FolderBase.owner_id == owner_id)
            .where(FolderBase.is_active)
            .options(joinedload(FolderBase.assistant).load_only(AssistantBase.name))
            .options(joinedload(FolderBase.chats))
            .options(joinedload(FolderBase.sources.of_type(sources)))
        )
        folder = await self._executor.execute_scalar_one(stmt)
        if not folder:
            raise NotFoundError(str(folder_id))
        return FolderReadMapper.to_read(folder)

    async def list_by_owner(self, owner_id: UUID) -> Sequence[FolderSummaryReadModel]:
        stmt = (
            select(FolderBase)
            .where(FolderBase.owner_id == owner_id)
            .where(FolderBase.is_active)
            .order_by(FolderBase.created_at.desc())
        )
        rows = await self._executor.execute_scalar_many(stmt)
        return [FolderReadMapper.to_summary(r) for r in rows]
