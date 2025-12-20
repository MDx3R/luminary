from collections.abc import AsyncGenerator
from typing import Final
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


ROLE_MAP: Final[dict[Author, MessageRole]] = {
    Author.SYSTEM: MessageRole.SYSTEM,
    Author.USER: MessageRole.USER,
    Author.ASSISTANT: MessageRole.ASSISTANT,
}


def build_filters(source_ids: list[UUID]) -> MetadataFilters:  # type: ignore
    return MetadataFilters(
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


def build_history(history: list[MessageDTO]) -> list[ChatMessage]:
    return [
        ChatMessage(
            content=msg.content,
            role=ROLE_MAP.get(msg.author, MessageRole.USER),
        )
        for msg in history
    ]


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
        filters = build_filters(source_ids)

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

        messages = [
            ChatMessage(content=system_prompt, role=MessageRole.SYSTEM),
            *build_history(history),
        ]

        user_content = (
            f"Context information:\n{context_str}\n\n"
            f"Query: {query}\nAnswer the query using the provided context information."
        )
        messages.append(ChatMessage(content=user_content, role=MessageRole.USER))

        streaming_response = await self.llm.astream_chat(messages)

        cumulative_tokens = 0
        async for chunk in streaming_response:
            delta = chunk.delta or ""
            cumulative_tokens += getattr(chunk, "tokens", 0)
            yield EngineStreamingResponse(
                content=delta, response_tokens=cumulative_tokens
            )


class ChatEngineLlamaIndexEngine(IEngine):
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
        filters = build_filters(source_ids)

        chat_engine = self.index.as_chat_engine(
            llm=self.llm,
            filters=filters,
            similarity_top_k=self.similarity_top_k,
            node_postprocessors=[
                SimilarityPostprocessor(similarity_cutoff=self.similarity_cutoff)
            ],
            text_qa_template=None,  # TODO: Свой template
        )

        messages = [
            ChatMessage(content=system_prompt, role=MessageRole.SYSTEM),
            *build_history(history),
        ]

        streaming_response = await chat_engine.astream_chat(query, messages)
        async_response_gen = streaming_response.async_response_gen()

        cumulative_tokens = 0
        async for chunk in async_response_gen:
            yield EngineStreamingResponse(
                content=chunk or "", response_tokens=cumulative_tokens
            )
