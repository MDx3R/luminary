from uuid import UUID

from common.domain.interfaces.clock import IClock
from common.domain.value_objects.id import UserId
from luminary_files.domain.entity.file import FileId

from luminary.content.application.exceptions import ParsingError
from luminary.content.application.interfaces.services.content_service import (
    IContentService,
    ProcessFileCommand,
)
from luminary.content.domain.entity.content import ContentId
from luminary.model.application.exceptions import EmbeddingError
from luminary.model.application.interfaces.repositories.vector_store import (
    VectorStoreMetadata,
)
from luminary.model.application.interfaces.services.embedding_service import (
    EmbedContentCommand,
    IEmbeddingService,
)
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.application.interfaces.usecases.command.create_source_use_case import (
    CreateFileSourceCommand,
    CreateLinkSourceCommand,
    CreatePageSourceCommand,
    ICreateFileSourceUseCase,
    ICreateLinkSourceUseCase,
    ICreatePageSourceUseCase,
)
from luminary.source.domain.interfaces.source_factory import (
    FileSourceFactoryDTO,
    ISourceFactory,
    LinkSourceFactoryDTO,
    PageSourceFactoryDTO,
)


class CreateFileSourceUseCase(ICreateFileSourceUseCase):
    def __init__(
        self,
        source_repository: ISourceRepository,
        source_factory: ISourceFactory,
    ) -> None:
        self.source_repository = source_repository
        self.source_factory = source_factory

    async def execute(self, command: CreateFileSourceCommand) -> UUID:
        # TODO: Consider different flow
        source = self.source_factory.create(
            FileSourceFactoryDTO(
                owner_id=UserId(command.user_id),
                title=command.title,
                file_id=FileId(command.file_id),
            )
        )
        await self.source_repository.add(source)
        return source.id.value


class CreateLinkSourceUseCase(ICreateLinkSourceUseCase):
    def __init__(
        self,
        source_repository: ISourceRepository,
        source_factory: ISourceFactory,
    ) -> None:
        self.source_repository = source_repository
        self.source_factory = source_factory

    async def execute(self, command: CreateLinkSourceCommand) -> UUID:
        source = self.source_factory.create(
            LinkSourceFactoryDTO(
                owner_id=UserId(command.user_id), title=command.title, url=command.url
            )
        )
        await self.source_repository.add(source)
        return source.id.value


class CreatePageSourceUseCase(ICreatePageSourceUseCase):
    def __init__(
        self,
        source_repository: ISourceRepository,
        source_factory: ISourceFactory,
        content_service: IContentService,
    ) -> None:
        self.source_repository = source_repository
        self.source_factory = source_factory
        self.content_service = content_service

    async def execute(self, command: CreatePageSourceCommand) -> UUID:
        user_id = command.user_id
        content_id = await self.content_service.process_file(
            ProcessFileCommand(user_id=user_id, data=command.data)
        )
        source = self.source_factory.create(
            PageSourceFactoryDTO(
                owner_id=UserId(user_id),
                title=command.title,
                content_id=ContentId(content_id),
            )
        )
        await self.source_repository.add(source)
        return source.id.value


class SyncCreateFileSourceUseCase(ICreateFileSourceUseCase):
    def __init__(
        self,
        clock: IClock,
        source_repository: ISourceRepository,
        source_factory: ISourceFactory,
        content_service: IContentService,
        embedding_service: IEmbeddingService,
    ) -> None:
        self.clock = clock
        self.source_repository = source_repository
        self.source_factory = source_factory
        self.content_service = content_service
        self.embedding_service = embedding_service

    async def execute(self, command: CreateFileSourceCommand) -> UUID:
        if not command.data:
            raise RuntimeError("data must be set")

        user_id = command.user_id

        source = self.source_factory.create(
            FileSourceFactoryDTO(
                owner_id=UserId(command.user_id),
                title=command.title,
                file_id=FileId(command.file_id),
            )
        )
        content_id = None
        try:
            content_id = await self.content_service.process_file(
                ProcessFileCommand(user_id=user_id, data=command.data)
            )
            source.fetch(ContentId(content_id), self.clock.now())
        except ParsingError:
            source.fail()

        try:
            if content_id:
                await self.embedding_service.embed_content(
                    EmbedContentCommand(
                        content_id=content_id,
                        metadata=VectorStoreMetadata(source_id=source.id.value),
                    )
                )
                source.embed()
        except EmbeddingError:
            source.fail()

        await self.source_repository.add(source)
        return source.id.value
