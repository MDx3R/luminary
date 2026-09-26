from dataclasses import dataclass

from common.domain.value_objects.id import EntityId


@dataclass(frozen=True)
class MessageId(EntityId): ...
