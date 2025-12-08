from abc import ABC, abstractmethod
from collections.abc import Iterable

from common.domain.events.event import Event


class IEventBus(ABC):
    @abstractmethod
    async def publish(self, event: Event) -> None: ...
    @abstractmethod
    async def publish_all(self, events: Iterable[Event]) -> None: ...
