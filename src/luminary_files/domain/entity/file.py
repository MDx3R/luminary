from dataclasses import dataclass
from typing import Self

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import EntityId, UserId


@dataclass(frozen=True)
class FileId(EntityId): ...


@dataclass
class File:
    id: FileId
    owner_id: UserId
    filename: str
    bucket: str
    object_key: str
    mime: str
    size: int
    uploaded_at: DateTime

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        id: FileId,
        owner_id: UserId,
        filename: str,
        bucket: str,
        mime: str,
        size: int,
        uploaded_at: DateTime,
    ) -> Self:
        return cls(
            id=id,
            owner_id=owner_id,
            filename=filename,
            bucket=bucket,
            object_key=str(id.value),
            mime=mime,
            size=size,
            uploaded_at=uploaded_at,
        )
