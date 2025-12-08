from dataclasses import dataclass

from common.domain.events.event import Event


@dataclass(frozen=True, kw_only=True)
class ApplicationEvent(Event): ...
