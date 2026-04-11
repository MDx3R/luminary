from common.application.interfaces.handlers.handler import IEventHandler
from common.domain.interfaces.clock import IClock

from luminary.content.application.interfaces.services.content_service import (
    GetContentQuery,
    IContentService,
)
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
from luminary.source.domain.entity.source import SourceId
from luminary.source.domain.events.events import SourceFetchedEvent


class SourceFetchedHandler(IEventHandler[SourceFetchedEvent]):
    def __init__(
        self,
        clock: IClock,
        source_repository: ISourceRepository,
        content_service: IContentService,
        embedding_service: IEmbeddingService,
    ) -> None:
        self.clock = clock
        self.source_repository = source_repository
        self.content_service = content_service
        self.embedding_service = embedding_service

    async def handle(self, event: SourceFetchedEvent) -> None:
        source = await self.source_repository.get_by_id(SourceId(event.source_id))

        if not source.can_be_embedded() or not source.content_id:
            return

        content = await self.content_service.get_content(
            GetContentQuery(
                user_id=source.owner_id.value, content_id=source.content_id.value
            )
        )

        try:
            await self.embedding_service.embed_content(
                EmbedContentCommand(
                    content=content,
                    metadata=VectorStoreMetadata(source_id=source.id.value),
                )
            )
            source.embed()
        except EmbeddingError:
            source.fail()

        await self.source_repository.save(source)
