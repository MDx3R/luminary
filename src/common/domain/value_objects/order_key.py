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


def order_key_between(previous: str | None, following: str | None) -> str:
    if previous is not None and following is not None and previous >= following:
        raise InvariantViolationError("Order neighbours must be distinct and ordered")
    return cast(str, generate_key_between(previous, following))
