from common.domain.value_objects.datetime import DateTime

from luminary.source.domain.entity.source import Source
from luminary.source.infrastructure.database.postgres.sqlalchemy.models.source_base import (
    SourceBase,
)


class SourceMapper:
    @classmethod
    def to_domain(cls, base: SourceBase) -> Source:
        return Source(
            source_id=base.source_id,
            user_id=base.user_id,
            name=base.name,
            created_at=DateTime(base.created_at),
        )

    @classmethod
    def to_persistence(cls, source: Source) -> SourceBase:
        return SourceBase(
            source_id=source.source_id,
            user_id=source.user_id,
            name=source.name,
            created_at=source.created_at.value,
        )
