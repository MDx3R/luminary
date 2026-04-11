from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator
from common.domain.value_objects.id import UserId

from luminary.content.domain.entity.content import Content, ContentId
from luminary.content.domain.interfaces.content_factory import IContentFactory


class ContentFactory(IContentFactory):
    def __init__(self, clock: IClock, uuid_generator: IUUIDGenerator) -> None:
        self.clock = clock
        self.uuid_generator = uuid_generator

    def create(self, user_id: UserId, bucket: str, mime: str, size: int) -> Content:
        return Content.create(
            ContentId(self.uuid_generator.create()),
            owner_id=user_id,
            bucket=bucket,
            mime=mime,
            size=size,
            uploaded_at=self.clock.now(),
        )
