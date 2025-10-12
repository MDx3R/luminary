from dataclasses import dataclass
from uuid import UUID

from common.domain.value_objects.datetime import DateTime


@dataclass
class Chat:
    chat_id: UUID
    environment_id: UUID
    created_at: DateTime
