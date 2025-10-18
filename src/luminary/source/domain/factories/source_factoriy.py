from uuid import UUID

from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.source.domain.entity.source import Source
from luminary.source.domain.interfaces.source_factory import ISourceFactory


class SourceFactory(ISourceFactory):
    def __init__(self, clock: IClock, uuid_generator: IUUIDGenerator) -> None:
        self.clock = clock
        self.uuid_generator = uuid_generator

    def create(
        self,
        user_id: UUID,
        filename: str,
        extension: str,
        mime: str,
    ) -> Source:
        return Source.create(
            source_id=self.uuid_generator.create(),
            user_id=user_id,
            filename=filename,
            extension=extension,
            mime=mime,
            created_at=self.clock.now(),
        )
