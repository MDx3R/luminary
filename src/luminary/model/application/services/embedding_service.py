from luminary.model.application.interfaces.repositories.vector_store import (
    IVectorStore,
)
from luminary.model.application.interfaces.services.embedding_service import (
    EmbedContentCommand,
    IEmbeddingService,
)


class EmbeddingService(IEmbeddingService):
    def __init__(self, vector_store: IVectorStore) -> None:
        self.vector_store = vector_store

    async def embed_content(self, command: EmbedContentCommand) -> None:
        data = command.content

        data.seek(0)
        await self.vector_store.save(data.read().decode(), command.metadata)
        data.seek(0)
