from dataclasses import dataclass
from typing import Self
from uuid import UUID

from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId
from common.domain.value_objects.title import Title

from luminary.source.domain.entity.source import Source, SourceId
from luminary.source.domain.enums import FetchStatus, SourceType


@dataclass
class PageSource(Source):
    editable: bool

    def __post_init__(self) -> None:
        if self.content_id is None:
            raise InvariantViolationError("Page source must always refer to content")
        if self.fetch_status != FetchStatus.FETCHED:
            raise InvariantViolationError("Page source must have fetched status")

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
        content_id: UUID,
        created_at: DateTime,
    ) -> Self:
        return cls(
            id=id,
            owner_id=owner_id,
            title=Title(title),
            type=SourceType.PAGE,
            content_id=content_id,
            fetch_status=FetchStatus.FETCHED,
            editable=True,
            fetched_at=created_at,
            created_at=created_at,
        )
