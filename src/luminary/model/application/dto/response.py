from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from luminary.model.application.dto.dto import OllamaChatMessage


class OllamaGenerateResponse(BaseModel):
    """Response model for Ollama generate endpoint."""

    model: str = Field(..., description="Model used for generation")
    created_at: str = Field(..., description="Creation timestamp")
    response: str = Field(..., description="Generated text")
    done: bool = Field(..., description="Whether generation is complete")
    done_reason: str | None = Field(None, description="Reason for completion")
    context: list[int] | None = Field(None, description="Updated context")
    total_duration: int | None = Field(
        None, description="Total duration in nanoseconds"
    )
    load_duration: int | None = Field(None, description="Model load duration")
    prompt_eval_count: int | None = Field(None, description="Tokens in prompt")
    prompt_eval_duration: int | None = Field(
        None, description="Prompt evaluation duration"
    )
    eval_count: int | None = Field(None, description="Tokens generated")
    eval_duration: int | None = Field(None, description="Generation duration")


OllamaStreamResponse = OllamaGenerateResponse


class OllamaChatResponse(BaseModel):
    """Response model for Ollama chat endpoint."""

    model: str = Field(..., description="Model used")
    created_at: str = Field(..., description="Creation timestamp")
    message: OllamaChatMessage = Field(..., description="Assistant's response message")
    done: bool = Field(..., description="Whether response is complete")
    done_reason: str | None = Field(None, description="Reason for completion")
    total_duration: int | None = Field(
        None, description="Total duration in nanoseconds"
    )
    load_duration: int | None = Field(None, description="Model load duration")
    prompt_eval_count: int | None = Field(None, description="Tokens in prompt")
    prompt_eval_duration: int | None = Field(
        None, description="Prompt evaluation duration"
    )
    eval_count: int | None = Field(None, description="Tokens generated")
    eval_duration: int | None = Field(None, description="Generation duration")


class OllamaModelInfo(BaseModel):
    """Model information for Ollama."""

    name: str = Field(..., description="Model name")
    model: str = Field(..., description="Model identifier")
    modified_at: str = Field(..., description="Last modified timestamp")
    size: int = Field(..., description="Model size in bytes")
    digest: str = Field(..., description="Model digest")
    details: dict[str, Any] | None = Field(None, description="Model details")
    expires_at: str | None = Field(None, description="Expiration timestamp")


class OllamaModelsResponse(BaseModel):
    """Response for model listing."""

    models: list[OllamaModelInfo] = Field(..., description="List of available models")


class OllamaShowResponse(BaseModel):
    """Response for showing model information."""

    model_config = ConfigDict(protected_namespaces=())

    modelfile: str = Field(..., description="Modelfile content")
    parameters: str = Field(..., description="Model parameters")
    template: str = Field(..., description="Model template")
    details: dict[str, Any] = Field(..., description="Model details")
    model_info: dict[str, Any] = Field(
        default_factory=dict, description="Additional model info"
    )


class OllamaVersionResponse(BaseModel):
    """Response for version endpoint."""

    version: str = Field(..., description="Ollama version")
