from dataclasses import dataclass
from typing import Self
from uuid import UUID

from common.domain.value_objects.datetime import DateTime


@dataclass
class Chat:
    chat_id: UUID
    folder_id: UUID
    created_at: DateTime

    @classmethod
    def create(
        cls,
        chat_id: UUID,
        folder_id: UUID,
        created_at: DateTime,
    ) -> Self:
        return cls(chat_id, folder_id, created_at)
