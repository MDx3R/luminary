import asyncio
from collections.abc import Iterable
from typing import Any

from common.application.interfaces.handlers.handler import EVENT, IEventHandler
from common.application.interfaces.services.event_bus import IEventBus
from common.domain.events.event import Event
from common.domain.interfaces.uuid_generator import IUUIDGenerator
from faststream import Logger
from faststream.rabbit import RabbitBroker, RabbitMessage, RabbitRoute
from pydantic import TypeAdapter, ValidationError
from pydantic.alias_generators import to_snake


class FastStreamRabbitMQEventBus(IEventBus):
    def __init__(
        self, broker: RabbitBroker, uuid_generator: IUUIDGenerator, prefix: str = ""
    ) -> None:
        self.broker = broker
        self.prefix = prefix
        self.uuid_generator = uuid_generator

    async def publish(self, event: Event) -> None:
        event = self.init_event(event)
        await self.broker.publish(  # pyright: ignore[reportUnknownMemberType]
            message=TypeAdapter[Any](type(event)).dump_python(event, mode="json"),
            queue=self.build_queue(self.prefix, type(event)),
        )

    async def publish_all(self, events: Iterable[Event]) -> None:
        await asyncio.gather(*[self.publish(e) for e in events])

    def init_event(self, event: EVENT) -> EVENT:
        return event.set_event_id(self.uuid_generator.create())

    @staticmethod
    def build_queue(prefix: str, event: type[Event]) -> str:
        entity_type = to_snake(event.aggregate_type())
        event_type = to_snake(event.event_type())
        return f"{prefix}.{entity_type}.{event_type}"

    @classmethod
    def build_route(
        cls, prefix: str, event_type: type[EVENT], handler: IEventHandler[EVENT]
    ) -> RabbitRoute:
        adapter = TypeAdapter[EVENT](event_type)

        async def wrapper(
            message_data: dict[str, Any], logger: Logger, msg: RabbitMessage
        ) -> None:
            logger.info(f"processing {event_type.event_type()}")

            try:
                event_data = adapter.validate_python(message_data)
            except ValidationError:
                logger.error(
                    f"validation failed for {event_type.event_type()} with data {message_data}"
                )
                await msg.reject()
                raise

            try:
                await handler.handle(event_data)
            except Exception:
                logger.error(f"handler failed for {event_type.event_type()}")
                await asyncio.sleep(3)
                await msg.nack(requeue=True)
                raise

        return RabbitRoute(wrapper, queue=cls.build_queue(prefix, event_type))
