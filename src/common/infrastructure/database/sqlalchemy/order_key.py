from datetime import datetime
from uuid import UUID

from common.domain.value_objects.order_key import (
    MAX_TIMESTAMP_MICROSECONDS,
    MICROSECONDS_PER_SECOND,
)
from sqlalchemy import BigInteger, ColumnElement, String, cast, func, literal


def effective_order_key(
    stored: ColumnElement[str | None],
    created_at: ColumnElement[datetime],
    entity_id: ColumnElement[UUID],
) -> ColumnElement[str]:
    """Build the SQL equivalent of initial_order_key using bytewise ordering."""
    timestamp = cast(
        func.extract("epoch", created_at) * MICROSECONDS_PER_SECOND, BigInteger
    )
    fallback = (
        literal("a0")
        + func.lpad(cast(MAX_TIMESTAMP_MICROSECONDS - timestamp, String), 18, "0")
        + func.replace(cast(entity_id, String), "-", "")
        + literal("V")
    )
    return func.coalesce(stored, fallback).collate("C")
