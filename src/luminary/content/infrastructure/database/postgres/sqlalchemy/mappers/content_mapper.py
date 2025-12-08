from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId
from common.domain.value_objects.object_key import ObjectKey

from luminary.content.domain.entity.content import Content, ContentId
from luminary.content.infrastructure.database.postgres.sqlalchemy.models.content_base import (
    ContentBase,
)


class ContentMapper:
    @classmethod
    def to_domain(cls, base: ContentBase) -> Content:
        return Content(
            id=ContentId(base.content_id),
            owner_id=UserId(base.user_id),
            bucket=base.bucket,
            object_key=ObjectKey(base.object_key),
            mime=base.mime,
            size=base.size,
            uploaded_at=DateTime(base.uploaded_at),
        )

    @classmethod
    def to_persistence(cls, content: Content) -> ContentBase:
        return ContentBase(
            content_id=content.id.value,
            user_id=content.owner_id.value,
            bucket=content.bucket,
            object_key=content.object_key.value,
            mime=content.mime,
            size=content.size,
            uploaded_at=content.uploaded_at.value,
        )
