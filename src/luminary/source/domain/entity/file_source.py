from dataclasses import dataclass
from typing import Self

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId
from common.domain.value_objects.title import Title
from luminary_files.domain.entity.file import FileId

from luminary.source.domain.entity.source import Source, SourceId
from luminary.source.domain.enums import FetchStatus, SourceType


@dataclass
class FileSource(Source):
    file_id: FileId

    @classmethod
    def create(
        cls,
        id: SourceId,
        owner_id: UserId,
        title: str,
        file_id: FileId,
        created_at: DateTime,
    ) -> Self:
        return cls(
            id=id,
            owner_id=owner_id,
            title=Title(title),
            content_id=None,
            fetched_at=None,
            fetch_status=FetchStatus.NOT_FETCHED,
            type=SourceType.FILE,
            file_id=file_id,
            created_at=created_at,
        )
