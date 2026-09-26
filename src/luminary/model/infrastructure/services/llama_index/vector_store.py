from llama_index.core import Document, VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.ingestion import arun_transformations
from llama_index.core.node_parser import (
    SemanticSplitterNodeParser,
    SentenceSplitter,
)

from luminary.model.application.exceptions import EmbeddingError
from luminary.model.application.interfaces.repositories.vector_store import (
    IVectorStore,
    VectorStoreMetadata,
)


# Stay under typical embedding API limit (e.g. 8192) so no node exceeds it
EMBED_MAX_TOKENS = 2048


# NOTE: Too expensive to use
class LlamaIndexSemanticSplitterVectorStore(IVectorStore):
    def __init__(self, index: VectorStoreIndex, embed_model: BaseEmbedding) -> None:
        self.index = index
        self.embed_model = embed_model

    async def save(self, content: str, metadata: VectorStoreMetadata) -> None:
        try:
            doc = Document(text=content, metadata=metadata.model_dump(mode="json"))

            # Chain: semantic split first, then enforce max chunk size (library pipeline)
            transformations = [
                SemanticSplitterNodeParser(
                    buffer_size=1,
                    breakpoint_percentile_threshold=95,
                    embed_model=self.embed_model,
                ),
                SentenceSplitter(
                    chunk_size=EMBED_MAX_TOKENS,
                    chunk_overlap=200,
                ),
            ]
            nodes = await arun_transformations([doc], transformations)

            await self.index.ainsert_nodes(nodes)
        except Exception as exc:
            raise EmbeddingError() from exc


class LlamaIndexSentenceSplitterVectorStore(IVectorStore):
    def __init__(self, index: VectorStoreIndex) -> None:
        self.index = index

    async def save(self, content: str, metadata: VectorStoreMetadata) -> None:
        try:
            doc = Document(text=content, metadata=metadata.model_dump(mode="json"))

            splitter = SentenceSplitter(
                chunk_size=EMBED_MAX_TOKENS,
                chunk_overlap=200,
            )
            nodes = await splitter.aget_nodes_from_documents([doc])

            await self.index.ainsert_nodes(nodes)
        except Exception as exc:
            raise EmbeddingError() from exc
