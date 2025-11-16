from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId
from luminary_files.domain.entity.file import File, FileId, ObjectKey
from luminary_files.infrastructure.database.postgres.sqlalchemy.models.file_base import (
    FileBase,
)


class FileMapper:
    @classmethod
    def to_domain(cls, base: FileBase) -> File:
        return File(
            id=FileId(base.file_id),
            owner_id=UserId(base.user_id),
            filename=base.filename,
            bucket=base.bucket,
            object_key=ObjectKey(base.object_key),
            mime=base.mime,
            size=base.size,
            uploaded_at=DateTime(base.uploaded_at),
        )

    @classmethod
    def to_persistence(cls, file: File) -> FileBase:
        return FileBase(
            file_id=file.id.value,
            user_id=file.owner_id.value,
            filename=file.filename,
            bucket=file.bucket,
            object_key=file.object_key.value,
            mime=file.mime,
            size=file.size,
            uploaded_at=file.uploaded_at.value,
        )
