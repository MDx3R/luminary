from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from luminary.model.application.interfaces.repositories.vector_store import (
    VectorStoreMetadata,
)


@dataclass(frozen=True)
class EmbedContentCommand:
    content_id: UUID
    metadata: VectorStoreMetadata


class IEmbeddingService(ABC):
    @abstractmethod
    async def embed_content(self, command: EmbedContentCommand) -> None: ...
