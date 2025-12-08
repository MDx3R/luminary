from collections.abc import AsyncGenerator
from uuid import UUID

from llama_cloud import FilterCondition, FilterOperator, MetadataFilter, MetadataFilters
from llama_index.core import VectorStoreIndex
from llama_index.core.llms import LLM, ChatMessage, MessageRole
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.retrievers import VectorIndexRetriever

from luminary.chat.application.interfaces.usecases.command.send_message_use_case import (
    MessageDTO,
)
from luminary.chat.domain.enums import Author
from luminary.model.application.interfaces.services.engine import (
    EngineStreamingResponse,
    IEngine,
)


class LlamaIndexEngine(IEngine):
    def __init__(
        self,
        llm: LLM,
        index: VectorStoreIndex,
        similarity_top_k: int = 5,
        similarity_cutoff: float = 0.7,
    ):
        self.llm = llm
        self.index = index
        self.similarity_top_k = similarity_top_k
        self.similarity_cutoff = similarity_cutoff

    async def send(
        self,
        query: str,
        *,
        system_prompt: str,
        source_ids: list[UUID],
        history: list[MessageDTO],
    ) -> AsyncGenerator[EngineStreamingResponse, None]:
        filters = None
        if source_ids:
            filters = MetadataFilters(
                filters=[
                    MetadataFilter(
                        key="source_id",
                        value=str(source_id),
                        operator=FilterOperator.EQUAL_TO,
                    )
                    for source_id in source_ids
                ],
                condition=FilterCondition.OR,
            )

        # Set up retriever with filters and postprocessor
        retriever = VectorIndexRetriever(
            index=self.index,
            filters=filters,
            similarity_top_k=self.similarity_top_k,
            node_postprocessors=[
                SimilarityPostprocessor(similarity_cutoff=self.similarity_cutoff)
            ],
        )

        # Retrieve relevant nodes asynchronously
        nodes = await retriever.aretrieve(query)

        # Build context string from retrieved nodes
        context_str = "\n\n".join([node.text for node in nodes])

        messages = [ChatMessage(content=system_prompt, role=MessageRole.SYSTEM)]
        for msg in history:
            role = (
                MessageRole.SYSTEM
                if msg.author == Author.SYSTEM
                else (
                    MessageRole.USER
                    if msg.author == Author.USER
                    else MessageRole.ASSISTANT
                )
            )
            messages.append(ChatMessage(content=msg.content, role=role))

        user_content = f"Context information: {context_str}\n\nQuery: {query}\nAnswer the query using the provided context information."
        messages.append(ChatMessage(content=user_content, role=MessageRole.USER))

        streaming_response = await self.llm.astream_chat(messages)

        cumulative_tokens = 0
        async for resp in streaming_response:
            yield EngineStreamingResponse(
                content=resp.delta or "", response_tokens=cumulative_tokens
            )
