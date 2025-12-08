from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest
import pytest_asyncio
from common.application.interfaces.handlers.handler import IEventHandler
from common.domain.interfaces.uuid_generator import IUUIDGenerator
from common.infrastructure.queues.faststream.event_bus import FastStreamRabbitMQEventBus
from faststream.rabbit import RabbitBroker, RabbitRouter, TestRabbitBroker
from tests.intergration.faststream.rabbitmq.conftest import PREFIX, MockEvent


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
        event = MockEvent(id=uuid4(), created_at=datetime.now())
        await self.event_bus.publish(event)

        event = self.event_bus.init_event(event)
        self.handler.handle.assert_awaited_once_with(event)

    async def test_publish_many_events(self) -> None:
        events = [MockEvent(id=uuid4(), created_at=datetime.now()) for _ in range(10)]
        await self.event_bus.publish_all(events)

        assert self.handler.handle.call_count == len(events)
