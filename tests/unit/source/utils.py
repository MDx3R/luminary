from datetime import UTC, datetime
from uuid import UUID, uuid4

from common.domain.value_objects.datetime import DateTime

from luminary.source.domain.entity.source import Source


def make_source(
    *,
    source_id: UUID | None = None,
    user_id: UUID | None = None,
    name: str = "Test Source",
    created_at: DateTime | None = None,
) -> Source:
    return Source(
        source_id=source_id or uuid4(),
        user_id=user_id or uuid4(),
        name=name,
        created_at=created_at or DateTime(datetime.now(UTC)),
    )
