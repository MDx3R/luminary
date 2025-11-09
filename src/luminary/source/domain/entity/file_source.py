from dataclasses import dataclass
from typing import Self
from uuid import UUID

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.title import Title

from luminary.source.domain.entity.source import Source
from luminary.source.domain.enums import SourceType
from luminary.source.domain.value_objects.file_meta import FileMeta


@dataclass
class FileSource(Source):
    meta: FileMeta

    @classmethod
    def create(
        cls,
        source_id: UUID,
        owner_id: UUID,
        title: str,
        meta: FileMeta,
        created_at: DateTime,
    ) -> Self:
        return cls(
            source_id=source_id,
            owner_id=owner_id,
            title=Title(title),
            content_id=None,
            type=SourceType.FILE,
            meta=meta,
            created_at=created_at,
        )
