from common.domain.value_objects.object_key import ObjectKey

from luminary.content.application.interfaces.repositories.content_storage import (
    IContentStorage,
)
from luminary.model.application.interfaces.repositories.vector_store import (
    IVectorStore,
)
from luminary.model.application.interfaces.services.embedding_service import (
    EmbedContentCommand,
    IEmbeddingService,
)


class EmbeddingService(IEmbeddingService):
    def __init__(
        self, content_storage: IContentStorage, vector_store: IVectorStore
    ) -> None:
        self.content_storage = content_storage
        self.vector_store = vector_store

    async def embed_content(self, command: EmbedContentCommand) -> None:
        content = await self.content_storage.get(ObjectKey(str(command.content_id)))
        await self.vector_store.save(content.read().decode(), command.metadata)
