from datetime import datetime

from common.domain.interfaces.clock import IClock
from common.domain.value_objects.datetime import DateTime


class SystemClock(IClock):
    def now(self) -> DateTime:
        return DateTime(datetime.now(self._tzinfo))


class FixedClock(IClock):
    def __init__(self, fixed_time: datetime):
        super().__init__()
        if fixed_time.tzinfo != self._tzinfo:
            fixed_time = fixed_time.replace(tzinfo=self._tzinfo)
        self._fixed_time = DateTime(fixed_time)

    def now(self) -> DateTime:
        return self._fixed_time
