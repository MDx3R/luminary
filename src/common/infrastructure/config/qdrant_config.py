from pydantic import BaseModel


class QdrantConfig(BaseModel):
    collection_name: str
    endpoint_url: str
    secret_key: str | None
    shutdown_grace: int = 5
    """Embedding vector dimension (e.g. 1536 for OpenAI text-embedding-3-small)."""
    vector_size: int = 1536
