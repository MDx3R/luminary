from dataclasses import dataclass
from typing import Self

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import EntityId, UserId
from common.domain.value_objects.object_key import ObjectKey
from luminary_files.domain.value_objects.file_meta import FileMeta


@dataclass(frozen=True)
class FileId(EntityId): ...


@dataclass
class File:
    id: FileId
    owner_id: UserId
    meta: FileMeta
    bucket: str
    object_key: ObjectKey
    uploaded_at: DateTime

    def is_owned_by(self, user_id: UserId) -> bool:
        return self.owner_id == user_id

    def specify_size(self, size: int) -> None:
        self.meta = FileMeta(
            filename=self.meta.filename, mime_type=self.meta.mime_type, filesize=size
        )

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        id: FileId,
        owner_id: UserId,
        filename: str,
        bucket: str,
        mime: str,
        uploaded_at: DateTime,
    ) -> Self:
        return cls(
            id=id,
            owner_id=owner_id,
            meta=FileMeta(filename=filename, mime_type=mime, filesize=None),
            bucket=bucket,
            object_key=ObjectKey(str(id.value)),
            uploaded_at=uploaded_at,
        )
