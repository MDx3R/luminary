import asyncio
from collections.abc import Iterable

from common.application.interfaces.handlers.handler import EVENT, IEventHandler
from common.application.interfaces.services.event_bus import IEventBus
from common.domain.events.event import Event
from faststream.rabbit import RabbitBroker, RabbitRoute
from pydantic.alias_generators import to_snake


class FastStreamRabbitMQEventBus(IEventBus):
    def __init__(self, broker: RabbitBroker, prefix: str = "") -> None:
        self.broker = broker
        self.prefix = prefix

    async def publish(self, event: Event) -> None:
        await self.broker.publish(  # pyright: ignore[reportUnknownMemberType]
            message=event, queue=self.build_queue(self.prefix, type(event))
        )

    async def publish_all(self, events: Iterable[Event]) -> None:
        await asyncio.gather(*[self.publish(e) for e in events])

    @staticmethod
    def build_queue(prefix: str, event: type[Event]) -> str:
        entity_type = to_snake(event.aggregate_type())
        event_type = to_snake(event.event_type())
        return f"{prefix}.{entity_type}.{event_type}"

    @classmethod
    def build_route(
        cls, prefix: str, event_type: type[EVENT], handler: IEventHandler[EVENT]
    ) -> RabbitRoute:
        async def wrapper(event: EVENT) -> None:
            await handler.handle(event)

        wrapper.__annotations__["event"] = event_type
        return RabbitRoute(wrapper, queue=cls.build_queue(prefix, event_type))
