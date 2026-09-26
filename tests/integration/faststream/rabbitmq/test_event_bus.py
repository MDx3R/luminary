from datetime import datetime
from unittest.mock import Mock, call
from uuid import uuid4

import pytest
import pytest_asyncio
from common.application.interfaces.handlers.handler import IEventHandler
from common.domain.interfaces.uuid_generator import IUUIDGenerator
from common.infrastructure.queues.faststream.event_bus import FastStreamRabbitMQEventBus
from faststream.rabbit import RabbitBroker, RabbitRouter, TestRabbitBroker
from tests.integration.faststream.rabbitmq.conftest import PREFIX, MockEvent


@pytest.mark.asyncio
class TestEventBus:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, broker: RabbitBroker):
        self.uuid_gen = Mock(spec=IUUIDGenerator, create=Mock(return_value=uuid4()))
        self.event_bus = FastStreamRabbitMQEventBus(
            broker, self.uuid_gen, prefix=PREFIX
        )

        self.handler = Mock(spec=IEventHandler[MockEvent])
        router = RabbitRouter(
            handlers=[self.event_bus.build_route(PREFIX, MockEvent, self.handler)]
        )
        broker.include_router(router)

        async with TestRabbitBroker(broker):
            yield

    async def test_publish_handle_event(self) -> None:
        # Arrange
        event = MockEvent(id=uuid4(), created_at=datetime.now())

        # Act
        await self.event_bus.publish(event)

        # Assert
        event = self.event_bus.init_event(event)
        self.handler.handle.assert_awaited_once_with(event)

    async def test_publish_many_events(self) -> None:
        # Arrange
        events = [MockEvent(id=uuid4(), created_at=datetime.now()) for _ in range(10)]

        # Act
        await self.event_bus.publish_all(events)

        # Assert
        events = [self.event_bus.init_event(e) for e in events]
        assert self.handler.handle.has_calls([call(e) for e in events])
