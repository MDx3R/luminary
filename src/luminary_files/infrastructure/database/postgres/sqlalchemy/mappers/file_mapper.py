from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId
from common.domain.value_objects.object_key import ObjectKey
from luminary_files.domain.entity.file import File, FileId
from luminary_files.domain.value_objects.file_meta import FileMeta
from luminary_files.infrastructure.database.postgres.sqlalchemy.models.file_base import (
    FileBase,
)


class FileMapper:
    @classmethod
    def to_domain(cls, base: FileBase) -> File:
        return File(
            id=FileId(base.file_id),
            owner_id=UserId(base.user_id),
            meta=FileMeta(
                filename=base.filename, mime_type=base.mime, filesize=base.size
            ),
            bucket=base.bucket,
            object_key=ObjectKey(base.object_key),
            uploaded_at=DateTime(base.uploaded_at),
        )

    @classmethod
    def to_persistence(cls, file: File) -> FileBase:
        size = file.meta.filesize if file.meta else None
        return FileBase(
            file_id=file.id.value,
            user_id=file.owner_id.value,
            filename=file.meta.filename,
            bucket=file.bucket,
            object_key=file.object_key.value,
            mime=file.meta.mime_type,
            size=size,
            uploaded_at=file.uploaded_at.value,
        )
