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


ROLE_MAP: Final[dict[Role, MessageRole]] = {
    Role.SYSTEM: MessageRole.SYSTEM,
    Role.USER: MessageRole.USER,
    Role.ASSISTANT: MessageRole.ASSISTANT,
}

LUMINARY_BASE_SYSTEM_PROMPT: Final[
    str
] = """You are a co-pilot in a human-centric intelligent workspace called Luminary. The user leads; you assist.

Your role: support the user's writing and analysis. 
Ground your answers in the sources and context provided with the request. 
Do not invent facts; when you use information from sources or context, rely on them and refer to them when helpful.

Constraints: do not replace the user's voice or make decisions for them. Offer options, check hypotheses, and help the user develop their own document. 
If the current request includes a "Current document (editor)" section, treat it as the user's working draft and help improve or extend it."""


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


def build_system_message(base_system_prompt: str, assistant_instructions: str) -> str:
    """Build system message: base role/task prompt + assistant instructions."""
    if not assistant_instructions or not assistant_instructions.strip():
        return base_system_prompt
    return (
        f"{base_system_prompt}\n\n---\n\nAssistant instructions:\n"
        f"{assistant_instructions}"
    )


def build_user_request_content(
    query: str,
    editor_content: str | None,
    rag_context_str: str | None = None,
) -> str:
    """Build the final user message: optional editor block, optional RAG context, query."""
    parts: list[str] = []
    if editor_content and editor_content.strip():
        parts.append(f"Current document (editor):\n{editor_content}")
    if rag_context_str and rag_context_str.strip():
        parts.append(f"Context information:\n{rag_context_str}")
    parts.append(
        f"Query: {query}\nAnswer the query using the provided context when relevant."
    )
    return "\n\n".join(parts)


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

        system_message = build_system_message(
            self.base_system_prompt, request.system_prompt
        )
        messages = [
            ChatMessage(content=system_message, role=MessageRole.SYSTEM),
            *build_history(request.history),
        ]

        user_content = build_user_request_content(
            request.query,
            request.editor_content,
            rag_context_str=context_str,
        )
        messages.append(ChatMessage(content=user_content, role=MessageRole.USER))

        streaming_response = await self.llm.astream_chat(messages)

        async for chunk in streaming_response:
            yield EngineStreamingResponse(content=chunk.delta or "")


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

        system_message = build_system_message(
            self.base_system_prompt, request.system_prompt
        )
        user_content = build_user_request_content(
            request.query, request.editor_content, rag_context_str=None
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
            yield EngineStreamingResponse(content=chunk or "")
