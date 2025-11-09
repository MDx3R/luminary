from dataclasses import dataclass
from typing import Self
from uuid import UUID

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.title import Title

from luminary.source.domain.entity.source import Source
from luminary.source.domain.enums import SourceType


@dataclass
class FileSource(Source):
    file_id: UUID

    @classmethod
    def create(
        cls,
        source_id: UUID,
        owner_id: UUID,
        title: str,
        file_id: UUID,
        created_at: DateTime,
    ) -> Self:
        return cls(
            source_id=source_id,
            owner_id=owner_id,
            title=Title(title),
            content_id=None,
            type=SourceType.FILE,
            file_id=file_id,
            created_at=created_at,
        )
