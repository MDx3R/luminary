import time
from collections.abc import AsyncGenerator
from datetime import datetime

from llama_index.core.llms import LLM, ChatMessage, MessageRole

from luminary.model.application.dto.dto import OllamaChatMessage
from luminary.model.application.dto.request import (
    OllamaChatRequest,
    OllamaGenerateRequest,
)
from luminary.model.application.dto.response import (
    OllamaChatResponse,
    OllamaGenerateResponse,
    OllamaModelInfo,
    OllamaModelsResponse,
)
from luminary.model.application.services.ollama_service import IOllamaService


class LlamaIndexOllamaServiceImpl(IOllamaService):
    def __init__(self, llm: LLM, model_name: str):
        self.llm = llm
        self.model_name = model_name

    async def list_models(self) -> OllamaModelsResponse:
        """List available models.

        This is a simplified implementation that returns the configured model.
        For full model listing, Ollama SDK or HTTP client would be needed.
        """
        model_info = OllamaModelInfo(
            name=self.model_name,
            model=self.model_name,
            modified_at=datetime.now().isoformat(),
            size=0,
            digest="",
            details=None,
            expires_at=None,
        )
        return OllamaModelsResponse(models=[model_info])

    async def generate(
        self, command: OllamaGenerateRequest
    ) -> AsyncGenerator[OllamaGenerateResponse]:
        messages = [
            ChatMessage(
                content=command.system or "",
                role=MessageRole.SYSTEM,
            ),
            ChatMessage(
                content=command.prompt,
                role=MessageRole.USER,
            ),
        ]

        start_time = time.time()
        streaming_response = await self.llm.astream_chat(messages)

        created_at = datetime.now().isoformat()
        prompt_eval_count = 0
        eval_count = 0
        token_count = 0

        async for chunk in streaming_response:
            if not chunk.delta:
                continue

            delta = chunk.delta or ""
            token_count += len(delta.split())

            yield OllamaGenerateResponse(
                model=command.model,
                created_at=created_at,
                response=delta,
                done=False,
                prompt_eval_count=None,
                eval_count=None,
                done_reason=None,
                context=None,
                total_duration=None,
                load_duration=None,
                prompt_eval_duration=None,
                eval_duration=None,
            )

        end_time = time.time()
        total_seconds = end_time - start_time
        total_duration_ns = int(total_seconds * 1_000_000_000)
        eval_duration_ns = int(total_duration_ns * 0.9)
        load_duration_ns = int(total_duration_ns * 0.05)
        prompt_eval_duration_ns = (
            total_duration_ns - eval_duration_ns - load_duration_ns
        )

        prompt_eval_count = 50
        eval_count = int(max(token_count * 1.3, 10))

        yield OllamaGenerateResponse(
            model=command.model,
            created_at=created_at,
            response="",
            done=True,
            done_reason="stop",
            prompt_eval_count=prompt_eval_count,
            eval_count=eval_count,
            context=None,
            total_duration=total_duration_ns,
            load_duration=load_duration_ns,
            prompt_eval_duration=prompt_eval_duration_ns,
            eval_duration=eval_duration_ns,
        )

    async def chat(
        self, command: OllamaChatRequest
    ) -> AsyncGenerator[OllamaChatResponse, None]:
        messages = [
            ChatMessage(
                content=msg.content,
                role=self._map_role(msg.role),
            )
            for msg in command.messages
        ]

        start_time = time.time()

        streaming_response = await self.llm.astream_chat(messages)

        created_at = datetime.now().isoformat()
        token_count = 0

        async for chunk in streaming_response:
            if not chunk.delta:
                continue

            delta = chunk.delta or ""
            token_count += len(delta.split())

            response_message = OllamaChatMessage(
                role="assistant", content=delta, images=[], tool_calls=[]
            )

            yield OllamaChatResponse(
                model=command.model,
                created_at=created_at,
                message=response_message,
                done=False,
                prompt_eval_count=None,
                eval_count=None,
                total_duration=None,
                load_duration=None,
                prompt_eval_duration=None,
                eval_duration=None,
                done_reason=None,
            )

        end_time = time.time()
        total_seconds = end_time - start_time
        total_duration_ns = int(total_seconds * 1_000_000_000)
        eval_duration_ns = int(total_duration_ns * 0.9)
        load_duration_ns = int(total_duration_ns * 0.05)
        prompt_eval_duration_ns = (
            total_duration_ns - eval_duration_ns - load_duration_ns
        )

        prompt_eval_count = 50
        eval_count = max(token_count * 1.3, 10)

        response_message = OllamaChatMessage(
            role="assistant", content="", images=[], tool_calls=[]
        )

        yield OllamaChatResponse(
            model=command.model,
            created_at=created_at,
            message=response_message,
            done=True,
            done_reason="stop",
            prompt_eval_count=int(prompt_eval_count),
            eval_count=int(eval_count),
            total_duration=total_duration_ns,
            load_duration=load_duration_ns,
            prompt_eval_duration=prompt_eval_duration_ns,
            eval_duration=eval_duration_ns,
        )

    @staticmethod
    def _map_role(role: str) -> MessageRole:
        """Map Ollama role string to LlamaIndex MessageRole."""
        role_map = {
            "system": MessageRole.SYSTEM,
            "user": MessageRole.USER,
            "assistant": MessageRole.ASSISTANT,
            "tool": MessageRole.TOOL,
        }
        return role_map.get(role, MessageRole.USER)
