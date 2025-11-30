import asyncio
from collections.abc import Iterable

from common.application.interfaces.services.event_bus import IEventBus
from common.domain.events.event import Event
from faststream.rabbit import RabbitBroker
from pydantic.alias_generators import to_snake


class FastStreamRabbitMQEventBus(IEventBus):
    def __init__(self, broker: RabbitBroker, prefix: str = "") -> None:
        self.broker = broker
        self.prefix = prefix

    async def publish(self, event: Event) -> None:
        await self.broker.publish(  # pyright: ignore[reportUnknownMemberType]
            message=event, queue=self.build_queue(event)
        )

    async def publish_all(self, events: Iterable[Event]) -> None:
        await asyncio.gather(*[self.publish(e) for e in events])

    def build_queue(self, event: Event) -> str:
        entity_type = to_snake(event.aggregate_type())
        event_type = to_snake(event.event_type())
        return f"{self.prefix}.{entity_type}.{event_type}"
