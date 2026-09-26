from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from common.domain.events.event import Event


EVENT = TypeVar("EVENT", bound=Event)


class IEventHandler(ABC, Generic[EVENT]):
    @abstractmethod
    async def handle(self, event: EVENT) -> None: ...
