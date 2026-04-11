from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetPresignedUrlQuery:
    user_id: UUID
    object_key: str
