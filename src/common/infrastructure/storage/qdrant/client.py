from typing import Self

from common.infrastructure.config.qdrant_config import QdrantConfig
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams


class QdrantStore:
    def __init__(self, client: AsyncQdrantClient, config: QdrantConfig):
        self._client = client
        self._config = config

    @classmethod
    def create(cls, config: QdrantConfig) -> Self:
        client = cls.create_client(config)
        return cls(client=client, config=config)

    @staticmethod
    def create_client(config: QdrantConfig) -> AsyncQdrantClient:
        return AsyncQdrantClient(config.endpoint_url, api_key=config.secret_key)

    def get_config(self) -> QdrantConfig:
        return self._config

    def get_client(self) -> AsyncQdrantClient:
        return self._client

    async def ensure_collection(self, vector_size: int | None = None) -> None:
        """Create the configured collection if it does not exist."""
        size = vector_size if vector_size is not None else self._config.vector_size

        if await self._client.collection_exists(self._config.collection_name):
            return

        await self._client.create_collection(
            collection_name=self._config.collection_name,
            vectors_config=VectorParams(size=size, distance=Distance.COSINE),
        )

    async def shutdown(self) -> None:
        await self._client.close(self._config.shutdown_grace)
