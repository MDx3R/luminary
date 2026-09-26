from abc import ABC, abstractmethod
from datetime import UTC, date, datetime, time, timezone

from common.domain.value_objects.datetime import DateTime  # timezone aware


class IClock(ABC):
    """Abstract base class for clock implementations.

    This class defines the interface for clock objects that provide timezone-aware
    date and time operations. Subclasses must implement the `now` method to return
    the current date and time as a `DateTime` object. The class also provides
    utility methods for working with timezones, combining date and time, and
    creating `DateTime` instances from timestamps.
    """

    def __init__(self) -> None:
        self._tzinfo = UTC

    @abstractmethod
    def now(self) -> DateTime: ...

    def timezone(self) -> timezone:
        return self._tzinfo

    def combine(self, date: date, time: time) -> DateTime:
        return DateTime(datetime.combine(date, time, tzinfo=time.tzinfo))

    def from_timestamp(self, timestamp: float) -> DateTime:
        return DateTime(datetime.fromtimestamp(timestamp, tz=self._tzinfo))
