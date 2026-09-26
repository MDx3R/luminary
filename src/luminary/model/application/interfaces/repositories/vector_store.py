from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import BaseModel


class VectorStoreMetadata(BaseModel):
    source_id: UUID


class IVectorStore(ABC):
    @abstractmethod
    async def save(self, content: str, metadata: VectorStoreMetadata) -> None: ...
