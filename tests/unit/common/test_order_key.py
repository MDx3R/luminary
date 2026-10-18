from datetime import UTC, datetime, timedelta
from itertools import pairwise
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


@pytest.mark.parametrize(
    "bounds",
    [
        (None, None),
        (None, "a0"),
        ("a0", None),
        ("a0", "a1"),
        ("a0", "a000000001"),
        ("Zz", "a0"),
        (None, "Zz"),
        (None, "a0V"),
        ("a0V", "a1V"),
    ],
)
def test_entity_keys_are_distinct_and_allow_further_insertion(bounds) -> None:
    previous, following = bounds
    keys = sorted(
        order_key_between(previous, following, UUID(int=i)) for i in range(20)
    )
    assert len(set(keys)) == len(keys)
    for key in keys:
        validate_order_key(key)
        assert previous is None or previous < key
        assert following is None or key < following
    for left, right in pairwise(keys):
        between = order_key_between(left, right, UUID(int=100))
        validate_order_key(between)
        assert left < between < right


def test_identity_suffix_is_stable_for_a_repeated_request() -> None:
    entity_id = UUID(int=1)
    assert order_key_between("a0", "a1", entity_id) == order_key_between(
        "a0", "a1", entity_id
    )
