from uuid import UUID

from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator
from common.domain.value_objects.datetime import DateTime


class MockUUIDGenerator(IUUIDGenerator):
    def __init__(self, uuid: UUID) -> None:
        self.uuid = uuid

    def create(self) -> UUID:
        return self.uuid


class MockClock(IClock):
    def __init__(self, current_time: DateTime) -> None:
        self._current_time = current_time

    def now(self) -> DateTime:
        return self._current_time
