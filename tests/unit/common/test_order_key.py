from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.order_key import initial_order_key, order_key_between
from fractional_indexing import validate_order_key


def test_initial_order_preserves_dates_and_uuid_ties() -> None:
    created = datetime(2026, 1, 1, tzinfo=UTC)
    first = initial_order_key(created, UUID(int=1))
    second = initial_order_key(created, UUID(int=2))
    newer = initial_order_key(created + timedelta(microseconds=1), UUID(int=3))
    assert newer < first < second
    for key in (newer, first, second):
        validate_order_key(key)


@pytest.mark.parametrize(
    "bounds", [(None, None), (None, "a0"), ("a0", None), ("a0", "a1")]
)
def test_key_between_neighbours(bounds) -> None:
    previous, following = bounds
    key = order_key_between(previous, following)
    assert previous is None or previous < key
    assert following is None or key < following
    validate_order_key(key)


@pytest.mark.parametrize("bounds", [("a0", "a0"), ("a1", "a0")])
def test_rejects_equal_or_reversed_bounds(bounds) -> None:
    with pytest.raises(InvariantViolationError):
        order_key_between(*bounds)
