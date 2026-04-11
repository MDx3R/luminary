from common.application.interfaces.handlers.handler import IEventHandler
from common.domain.interfaces.clock import IClock
from luminary_files.application.interfaces.services.file_service import (
    GetFileQuery,
    IFileService,
)

from luminary.content.application.exceptions import ParsingError
from luminary.content.application.interfaces.services.content_service import (
    IContentService,
    ProcessFileCommand,
    ProcessLinkCommand,
)
from luminary.content.domain.entity.content import ContentId
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.domain.entity.file_source import FileSource
from luminary.source.domain.entity.link_source import LinkSource
from luminary.source.domain.entity.page_source import PageSource
from luminary.source.domain.entity.source import SourceId
from luminary.source.domain.enums import FetchStatus
from luminary.source.domain.events.events import SourceCreatedEvent


class SourceCreatedHandler(IEventHandler[SourceCreatedEvent]):
    def __init__(
        self,
        clock: IClock,
        source_repository: ISourceRepository,
        content_service: IContentService,
        file_service: IFileService,
    ) -> None:
        self.clock = clock
        self.source_repository = source_repository
        self.content_service = content_service
        self.file_service = file_service

    async def handle(self, event: SourceCreatedEvent) -> None:
        if event.fetch_status != FetchStatus.NOT_FETCHED:
            return

        source = await self.source_repository.get_by_id(SourceId(event.source_id))

        if not source.can_be_fetched():
            return

        match source:
            case FileSource():
                await self.handle_file(source)
            case LinkSource():
                await self.handle_link(source)
            case PageSource():
                await self.handle_page(source)
            case _:
                # TODO: Unknown source type, do nothing or log
                return

        await self.source_repository.save(source)

    async def handle_page(self, source: PageSource) -> None:
        return

    async def handle_file(self, source: FileSource) -> None:
        user_id = source.owner_id.value

        data = await self.file_service.get_file(
            GetFileQuery(user_id=user_id, file_id=source.file_id.value)
        )

        try:
            content_id = await self.content_service.process_file(
                ProcessFileCommand(
                    user_id=source.owner_id.value,
                    data=data,
                    filename=source.title.value,
                )
            )
            source.fetch(ContentId(content_id), self.clock.now())
        except ParsingError:
            source.fail()

    async def handle_link(self, source: LinkSource) -> None:
        try:
            content_id = await self.content_service.process_link(
                ProcessLinkCommand(user_id=source.owner_id.value, url=source.url.value)
            )
            source.fetch(ContentId(content_id), self.clock.now())
        except ParsingError:
            source.fail()
