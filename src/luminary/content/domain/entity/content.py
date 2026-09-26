from dataclasses import dataclass
from typing import Self

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import EntityId, UserId
from common.domain.value_objects.object_key import ObjectKey


@dataclass(frozen=True)
class ContentId(EntityId): ...


@dataclass
class Content:
    id: ContentId
    owner_id: UserId
    bucket: str
    object_key: ObjectKey
    mime: str
    size: int
    uploaded_at: DateTime

    def is_owned_by(self, user_id: UserId) -> bool:
        return self.owner_id == user_id

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        id: ContentId,
        owner_id: UserId,
        bucket: str,
        mime: str,
        size: int,
        uploaded_at: DateTime,
    ) -> Self:
        return cls(
            id=id,
            owner_id=owner_id,
            bucket=bucket,
            object_key=ObjectKey(str(id.value)),
            mime=mime,
            size=size,
            uploaded_at=uploaded_at,
        )
