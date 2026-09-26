from abc import ABC
from dataclasses import dataclass, field

from common.domain.events.domain_event import DomainEvent


@dataclass(kw_only=True)
class Entity(ABC):  # noqa: B024
    _events: list[DomainEvent] = field(
        default_factory=list[DomainEvent], init=False, repr=False, compare=False
    )

    @property
    def events(self) -> list[DomainEvent]:
        return self._events.copy()

    def _record_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def has_changes(self) -> bool:
        return bool(self._events)
