from functools import singledispatchmethod
from typing import Any, final

from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.source.domain.entity.file_source import FileSource
from luminary.source.domain.entity.link_source import LinkSource
from luminary.source.domain.entity.page_source import PageSource
from luminary.source.domain.entity.source import Source, SourceId
from luminary.source.domain.interfaces.source_factory import (
    FileSourceFactoryDTO,
    ISourceFactory,
    LinkSourceFactoryDTO,
    PageSourceFactoryDTO,
)


class SourceFactory(ISourceFactory):
    @final
    class _Dispatcher:
        def __init__(self, clock: IClock, uuid_generator: IUUIDGenerator) -> None:
            self.clock = clock
            self.uuid_generator = uuid_generator

        @singledispatchmethod
        def create(self, data: Any) -> Source:
            raise TypeError(f"Unsupported DTO type: {type(data).__name__}")

        @create.register
        def _(self, data: FileSourceFactoryDTO) -> FileSource:
            return FileSource.create(
                id=SourceId(self.uuid_generator.create()),
                owner_id=data.owner_id,
                title=data.title,
                created_at=self.clock.now(),
                file_id=data.file_id,
            )

        @create.register
        def _(self, data: LinkSourceFactoryDTO) -> LinkSource:
            return LinkSource.create(
                id=SourceId(self.uuid_generator.create()),
                owner_id=data.owner_id,
                title=data.title,
                created_at=self.clock.now(),
                url=data.url,
            )

        @create.register
        def _(self, data: PageSourceFactoryDTO) -> PageSource:
            return PageSource.create(
                id=SourceId(self.uuid_generator.create()),
                owner_id=data.owner_id,
                title=data.title,
                content_id=data.content_id,
                created_at=self.clock.now(),
            )

    def __init__(self, clock: IClock, uuid_generator: IUUIDGenerator) -> None:
        self.dispatch_factory = self._Dispatcher(clock, uuid_generator)

    def create(
        self, data: FileSourceFactoryDTO | LinkSourceFactoryDTO | PageSourceFactoryDTO
    ) -> Source:
        return self.dispatch_factory.create(data)
