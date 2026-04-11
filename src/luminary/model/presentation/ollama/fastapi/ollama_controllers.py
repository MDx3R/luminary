from collections.abc import AsyncGenerator
from datetime import datetime

from common.presentation.http.fastapi.cbv import cbv
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse, StreamingResponse

from luminary.model.application.dto.dto import OllamaChatMessage
from luminary.model.application.dto.request import (
    OllamaChatRequest,
    OllamaGenerateRequest,
    OllamaShowRequest,
)
from luminary.model.application.dto.response import (
    OllamaChatResponse,
    OllamaGenerateResponse,
    OllamaModelsResponse,
    OllamaVersionResponse,
)
from luminary.model.application.services.ollama_service import IOllamaService


ollama_router = APIRouter()


@cbv(ollama_router)
class OllamaController:
    ollama_service: IOllamaService = Depends()

    @ollama_router.get("/")
    async def healtcheck(self) -> JSONResponse:
        return JSONResponse(
            content={
                "status": "healthy",
                "version": "0.0.0",
                "timestamp": datetime.now().isoformat(),
                "service": "luminary-ollama",
            }
        )

    @ollama_router.get("/tags")
    async def list_models(self) -> OllamaModelsResponse:
        return await self.ollama_service.list_models()

    @ollama_router.post("/pull")
    async def pull_model(self) -> None:
        self._raise_not_implemented()

    @ollama_router.delete("/delete")
    async def delete_model(self) -> None:
        self._raise_not_implemented()

    @ollama_router.post("/copy")
    async def copy_model(self) -> None:
        self._raise_not_implemented()

    @ollama_router.post("/generate")
    async def generate(self, request: OllamaGenerateRequest) -> Response:
        gen = self.ollama_service.generate(request)

        # STREAMING
        if request.stream:

            async def stream() -> AsyncGenerator[str]:
                async for chunk in gen:
                    yield chunk.model_dump_json(exclude_none=True) + "\n"  # NDJSON

            return StreamingResponse(stream(), media_type="application/x-ndjson")

        # NON-STREAM
        last = await self._collect_generate(gen)
        if last is None:
            raise self._get_no_response_exc()

        return JSONResponse(content=last.model_dump())

    @ollama_router.post("/chat")
    async def chat(self, request: OllamaChatRequest) -> Response:
        gen = self.ollama_service.chat(request)

        # STREAMING
        if request.stream:

            async def stream() -> AsyncGenerator[str]:
                async for chunk in gen:
                    yield chunk.model_dump_json(exclude_none=True) + "\n"  # NDJSON

            return StreamingResponse(stream(), media_type="application/x-ndjson")

        # NON-STREAM
        last = await self._collect_chat(gen)
        if last is None:
            raise self._get_no_response_exc()

        return JSONResponse(content=last.model_dump())

    @ollama_router.post("/embeddings")
    async def embeddings(self) -> None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Embeddings are not supported yet.",
        )

    @ollama_router.get("/show")
    async def show_model(self, request: OllamaShowRequest) -> None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Show is not supported yet.",
        )

    @ollama_router.post("/version")
    async def get_version(self) -> OllamaVersionResponse:
        # NOTE: This looks like valid version but whatever
        return OllamaVersionResponse(version="0.1.42")

    def _raise_not_implemented(self) -> None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Model management operations (pull/push/delete/copy) are not supported by the OpenAI-compatible backend",
        )

    async def _collect_chat(
        self, gen: AsyncGenerator[OllamaChatResponse]
    ) -> OllamaChatResponse | None:
        # NOTE: Since service is meant to use streaming response format
        # regardless of request.stream value,
        # here we should aggregate results properly

        full_content = ""
        last = None

        async for chunk in gen:
            delta = chunk.message.content or ""
            full_content += delta
            last = chunk

        if last is None:
            return None

        aggregated_message = OllamaChatMessage(
            role="assistant",
            content=full_content,
            images=[],
            tool_calls=[],
        )

        return OllamaChatResponse(
            model=last.model,
            created_at=last.created_at,
            message=aggregated_message,
            done=True,
            done_reason="stop",
            total_duration=last.total_duration,
            load_duration=last.load_duration,
            prompt_eval_count=last.prompt_eval_count,
            prompt_eval_duration=last.prompt_eval_duration,
            eval_count=last.eval_count,
            eval_duration=last.eval_duration,
        )

    async def _collect_generate(
        self, gen: AsyncGenerator[OllamaGenerateResponse]
    ) -> OllamaGenerateResponse | None:
        full_response = ""
        last = None

        async for chunk in gen:
            delta = chunk.response or ""
            full_response += delta
            last = chunk

        if last is None:
            return None

        return OllamaGenerateResponse(
            model=last.model,
            created_at=last.created_at,
            response=full_response,
            done=True,
            done_reason="stop",
            context=last.context,
            total_duration=last.total_duration,
            load_duration=last.load_duration,
            prompt_eval_count=last.prompt_eval_count,
            prompt_eval_duration=last.prompt_eval_duration,
            eval_duration=last.eval_duration,
            eval_count=last.eval_count,
        )

    def _get_no_response_exc(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Response produced no content.",
        )
