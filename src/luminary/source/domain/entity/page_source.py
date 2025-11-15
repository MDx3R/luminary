from dataclasses import dataclass
from typing import Self

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId
from common.domain.value_objects.title import Title

from luminary.source.domain.entity.source import Source, SourceId
from luminary.source.domain.enums import SourceType


@dataclass
class PageSource(Source):
    editable: bool

    def is_content_editable(self) -> bool:
        return self.editable

    def lock(self) -> None:
        self.editable = False

    def unlock(self) -> None:
        self.editable = True

    @classmethod
    def create(
        cls,
        id: SourceId,
        owner_id: UserId,
        title: str,
        created_at: DateTime,
    ) -> Self:
        return cls(
            id=id,
            owner_id=owner_id,
            title=Title(title),
            type=SourceType.PAGE,
            content_id=None,
            editable=True,
            created_at=created_at,
        )
