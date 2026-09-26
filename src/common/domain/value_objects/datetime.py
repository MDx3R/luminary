from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta, timezone
from typing import Any

from common.domain.exceptions import InvariantViolationError


@dataclass(frozen=True)
class DateTime:
    """A value object representing a timezone-aware datetime."""

    value: datetime

    def __post_init__(self) -> None:
        tzinfo = self.value.tzinfo
        if tzinfo is None or tzinfo.utcoffset(self.value) is None:
            raise InvariantViolationError("DateTime must be timezone-aware")

    def isoformat(self) -> str:
        return self.value.isoformat()

    def astimezone(self, tz: timezone | None = None) -> "DateTime":
        return DateTime(self.value.astimezone(tz))

    def date(self) -> date:
        return self.value.date()

    def time(self) -> time:
        return self.value.time()

    def timestamp(self) -> float:
        return self.value.timestamp()

    def to_utc(self) -> "DateTime":
        return self.astimezone(UTC)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, DateTime):
            return self.value == other.value
        if isinstance(other, datetime):
            return self.value == other
        return NotImplemented

    def __ne__(self, other: Any) -> bool:
        if isinstance(other, DateTime):
            return self.value != other.value
        if isinstance(other, datetime):
            return self.value != other
        return NotImplemented

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, DateTime):
            return self.value < other.value
        if isinstance(other, datetime):
            return self.value < other
        return NotImplemented

    def __le__(self, other: Any) -> bool:
        if isinstance(other, DateTime):
            return self.value <= other.value
        if isinstance(other, datetime):
            return self.value <= other
        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, DateTime):
            return self.value > other.value
        if isinstance(other, datetime):
            return self.value > other
        return NotImplemented

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, DateTime):
            return self.value >= other.value
        if isinstance(other, datetime):
            return self.value >= other
        return NotImplemented

    def __add__(self, other: Any) -> "DateTime":
        if isinstance(other, timedelta):
            return DateTime(self.value + other)
        return NotImplemented

    def __sub__(self, other: Any) -> Any:
        if isinstance(other, timedelta):
            return DateTime(self.value - other)
        if isinstance(other, DateTime):
            return self.value - other.value
        if isinstance(other, datetime):
            return self.value - other
        return NotImplemented

    def __hash__(self) -> Any:
        return hash(self.value)
