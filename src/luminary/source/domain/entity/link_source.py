from dataclasses import dataclass
from typing import Self

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId
from common.domain.value_objects.title import Title
from common.domain.value_objects.url import Url

from luminary.source.domain.entity.source import Source, SourceId
from luminary.source.domain.enums import FetchStatus, SourceType
from luminary.source.domain.events.events import SourceCreatedEvent


@dataclass
class LinkSource(Source):
    url: Url

    @classmethod
    def create(
        cls,
        id: SourceId,
        owner_id: UserId,
        title: str,
        url: str,
        created_at: DateTime,
    ) -> Self:
        page = cls(
            id=id,
            owner_id=owner_id,
            title=Title(title),
            type=SourceType.LINK,
            url=Url(url),
            content_id=None,
            fetched_at=None,
            fetch_status=FetchStatus.NOT_FETCHED,
            created_at=created_at,
        )
        page._record_event(
            SourceCreatedEvent(source_id=id.value, fetch_status=page.fetch_status)
        )

        return page
