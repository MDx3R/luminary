from collections.abc import AsyncGenerator, Sequence
from typing import Final
from uuid import UUID

from llama_index.core import VectorStoreIndex
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.llms import LLM, MessageRole
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import NodeWithScore
from llama_index.core.vector_stores.types import (
    FilterCondition,
    FilterOperator,
    MetadataFilter,
    MetadataFilters,
)

from luminary.model.application.interfaces.services.engine import (
    EngineStreamingResponse,
    IInferenceEngine,
    InferenceRequestDTO,
    MessageDTO,
    Role,
)
from luminary.model.application.prompts import (
    LUMINARY_BASE_SYSTEM_PROMPT,
    build_user_request_content,
    render_final_system_prompt,
)


ROLE_MAP: Final[dict[Role, MessageRole]] = {
    Role.SYSTEM: MessageRole.SYSTEM,
    Role.USER: MessageRole.USER,
    Role.ASSISTANT: MessageRole.ASSISTANT,
}


def build_filters(source_ids: Sequence[UUID]) -> MetadataFilters:
    """Build metadata filters for vector store index: source_id in (id1 or id2 or ...)."""
    return MetadataFilters(
        filters=[
            MetadataFilter(
                key="source_id",
                value=str(source_id),
                operator=FilterOperator.EQ,
            )
            for source_id in source_ids
        ],
        condition=FilterCondition.OR,
    )


def build_history(history: Sequence[MessageDTO]) -> Sequence[ChatMessage]:
    return [
        ChatMessage(
            content=msg.content,
            role=ROLE_MAP.get(msg.role, MessageRole.USER),
        )
        for msg in history
    ]


class LlamaIndexEngine(IInferenceEngine):
    def __init__(
        self,
        llm: LLM,
        index: VectorStoreIndex,
        base_system_prompt: str = LUMINARY_BASE_SYSTEM_PROMPT,
        similarity_top_k: int = 5,
        similarity_cutoff: float = 0.7,
    ):
        self.llm = llm
        self.index = index
        self.base_system_prompt = base_system_prompt
        self.similarity_top_k = similarity_top_k
        self.similarity_cutoff = similarity_cutoff

    async def send(
        self, request: InferenceRequestDTO
    ) -> AsyncGenerator[EngineStreamingResponse, None]:
        if request.source_ids:
            filters = build_filters(request.source_ids)

            retriever = VectorIndexRetriever(
                index=self.index,
                filters=filters,
                similarity_top_k=self.similarity_top_k,
                node_postprocessors=[
                    SimilarityPostprocessor(similarity_cutoff=self.similarity_cutoff)
                ],
            )

            nodes = await retriever.aretrieve(request.query)
        else:
            nodes = list[NodeWithScore]()

        context_str = "\n\n".join([node.text for node in nodes])

        system_message = render_final_system_prompt(self.base_system_prompt, request)
        messages = [
            ChatMessage(content=system_message, role=MessageRole.SYSTEM),
            *build_history(request.history),
        ]

        user_content = build_user_request_content(
            request.query,
            request.editor_content,
            rag_context_str=context_str,
            mode=request.mode,
        )
        messages.append(ChatMessage(content=user_content, role=MessageRole.USER))

        streaming_response = await self.llm.astream_chat(messages)

        async for chunk in streaming_response:
            if not chunk.delta:
                continue
            yield EngineStreamingResponse(content=chunk.delta)


class ChatEngineLlamaIndexEngine(IInferenceEngine):
    def __init__(  # noqa: PLR0913
        self,
        llm: LLM,
        index: VectorStoreIndex,
        base_system_prompt: str = LUMINARY_BASE_SYSTEM_PROMPT,
        similarity_top_k: int = 5,
        similarity_cutoff: float = 0.7,
        inference_fallback: IInferenceEngine | None = None,
    ):
        self.llm = llm
        self.index = index
        self.base_system_prompt = base_system_prompt
        self.similarity_top_k = similarity_top_k
        self.similarity_cutoff = similarity_cutoff

        if inference_fallback is not None:
            self.inference_fallback = inference_fallback
        else:
            self.inference_fallback = LlamaIndexEngine(
                llm,
                index,
                base_system_prompt,
                similarity_top_k=similarity_top_k,
                similarity_cutoff=similarity_cutoff,
            )

    async def send(
        self, request: InferenceRequestDTO
    ) -> AsyncGenerator[EngineStreamingResponse, None]:
        if not request.source_ids:
            async_response_gen = self.inference_fallback.send(request)

            async for chunk in async_response_gen:
                yield chunk

            return

        system_message = render_final_system_prompt(self.base_system_prompt, request)
        user_content = build_user_request_content(
            request.query,
            request.editor_content,
            rag_context_str=None,
            mode=request.mode,
        )

        chat_history = list[ChatMessage](build_history(request.history))

        filters = build_filters(request.source_ids)
        retriever = VectorIndexRetriever(
            index=self.index,
            filters=filters,
            similarity_top_k=self.similarity_top_k,
            node_postprocessors=[
                SimilarityPostprocessor(similarity_cutoff=self.similarity_cutoff)
            ],
        )

        chat_engine = CondensePlusContextChatEngine.from_defaults(
            retriever=retriever,
            llm=self.llm,
            system_prompt=system_message,
            chat_history=chat_history,
        )

        streaming_response = await chat_engine.astream_chat(
            user_content, chat_history=chat_history
        )
        async_response_gen = streaming_response.async_response_gen()

        async for chunk in async_response_gen:
            if not chunk:
                continue
            yield EngineStreamingResponse(content=chunk)
