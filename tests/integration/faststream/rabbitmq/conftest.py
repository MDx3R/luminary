from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import pytest
from common.domain.events.event import Event
from faststream.rabbit import RabbitBroker


PREFIX = "testing"


@dataclass(frozen=True)
class MockEvent(Event):
    id: UUID
    created_at: datetime

    @property
    def aggregate_id(self) -> UUID:
        return self.id

    @classmethod
    def aggregate_type(cls) -> str:
        return "mock"


@pytest.fixture(scope="session")
def broker():
    return RabbitBroker()
