from datetime import UTC, datetime
from typing import cast
from uuid import UUID

from common.domain.exceptions import InvariantViolationError
from fractional_indexing import generate_key_between


MAX_TIMESTAMP_MICROSECONDS = 999_999_999_999_999_999
MICROSECONDS_PER_SECOND = 1_000_000
SECONDS_PER_DAY = 86_400


def initial_order_key(created_at: datetime, entity_id: UUID) -> str:
    """Preserve created_at DESC, id ASC without backfilling existing rows."""
    delta = created_at - datetime(1970, 1, 1, tzinfo=UTC)
    microseconds = (
        delta.days * SECONDS_PER_DAY + delta.seconds
    ) * MICROSECONDS_PER_SECOND + delta.microseconds
    # A valid fractional suffix must not end in zero. UUID breaks timestamp ties.
    return f"a0{MAX_TIMESTAMP_MICROSECONDS - microseconds:018d}{entity_id.hex}V"


def order_key_between(
    previous: str | None, following: str | None, entity_id: UUID | None = None
) -> str:
    if previous is not None and following is not None and previous >= following:
        raise InvariantViolationError("Order neighbours must be distinct and ordered")
    key = cast(str, generate_key_between(previous, following))
    if entity_id is None:
        return key
    # A fixed-width identity suffix makes keys of different entities distinct,
    # even when requests use the same (possibly stale) neighbour pair. First
    # leave the upper bound's prefix so appending cannot cross that bound.
    while following is not None and following.startswith(key):
        key = cast(str, generate_key_between(key, following))
    return f"{key}{entity_id.hex}V"
