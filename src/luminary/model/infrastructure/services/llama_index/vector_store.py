from uuid import uuid4

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.node_parser import SemanticSplitterNodeParser

from luminary.model.application.interfaces.repositories.vector_store import IVectorStore


class LlamaIndexEngineVectorStore(IVectorStore):
    def __init__(self, index: VectorStoreIndex, embed_model: BaseEmbedding) -> None:
        self.index = index
        self.embed_model = embed_model

    async def save(self, content: str) -> None:
        source_id = uuid4()
        doc = Document(text=content, metadata={"source_id": str(source_id)})

        splitter = SemanticSplitterNodeParser(
            buffer_size=1,
            breakpoint_percentile_threshold=95,
            embed_model=self.embed_model,
        )
        nodes = await splitter.aget_nodes_from_documents([doc])

        await self.index.ainsert_nodes(nodes)
