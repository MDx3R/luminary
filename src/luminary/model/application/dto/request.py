from typing import Any, Literal, Self

from pydantic import BaseModel, Field, model_validator

from luminary.model.application.dto.dto import OllamaChatMessage


class OllamaOptions(BaseModel):
    """Options for Ollama model inference."""

    # Generation parameters
    seed: int | None = Field(None, description="Random seed for generation")
    num_predict: int | None = Field(
        None, description="Maximum number of tokens to predict"
    )
    top_k: int | None = Field(None, description="Top-k sampling parameter")
    top_p: float | None = Field(
        None, ge=0.0, le=1.0, description="Top-p (nucleus) sampling"
    )
    tfs_z: float | None = Field(None, description="Tail free sampling parameter")
    typical_p: float | None = Field(
        None, ge=0.0, le=1.0, description="Typical sampling parameter"
    )
    repeat_last_n: int | None = Field(
        None, description="Last n tokens to consider for repeat penalty"
    )
    temperature: float | None = Field(None, ge=0.0, description="Sampling temperature")
    repeat_penalty: float | None = Field(None, description="Repeat penalty parameter")
    presence_penalty: float | None = Field(
        None, description="Presence penalty parameter"
    )
    frequency_penalty: float | None = Field(
        None, description="Frequency penalty parameter"
    )
    mirostat: int | None = Field(None, description="Mirostat sampling mode (0/1/2)")
    mirostat_tau: float | None = Field(None, description="Mirostat target entropy")
    mirostat_eta: float | None = Field(None, description="Mirostat learning rate")
    penalize_newline: bool | None = Field(
        None, description="Whether to penalize newlines"
    )
    stop: list[str] | None = Field(None, description="Stop sequences")

    # Model loading parameters
    numa: bool | None = Field(None, description="Enable NUMA support")
    num_ctx: int | None = Field(None, description="Context window size")
    num_batch: int | None = Field(None, description="Batch size for prompt processing")
    num_gqa: int | None = Field(None, description="Number of GQA groups")
    num_gpu: int | None = Field(None, description="Number of layers to offload to GPU")
    main_gpu: int | None = Field(None, description="Main GPU to use")
    low_vram: bool | None = Field(None, description="Enable low VRAM mode")
    f16_kv: bool | None = Field(None, description="Use 16-bit floats for KV cache")
    vocab_only: bool | None = Field(None, description="Load vocabulary only")
    use_mmap: bool | None = Field(None, description="Use memory mapping for model")
    use_mlock: bool | None = Field(None, description="Lock model in memory")
    num_thread: int | None = Field(None, description="Number of threads to use")


class OllamaGenerateRequest(BaseModel):
    """Request model for Ollama generate endpoint."""

    model: str = Field(..., description="Model name to use for generation")
    prompt: str = Field(..., description="Input prompt for generation")
    images: list[str] | None = Field(None, description="Base64 encoded images")
    format: Literal["json"] | None = Field(None, description="Response format")
    options: OllamaOptions | None = Field(None, description="Model options")
    system: str | None = Field(None, description="System prompt")
    template: str | None = Field(None, description="Prompt template")
    context: list[int] | None = Field(None, description="Conversation context")
    stream: bool = Field(True, description="Stream response")
    raw: bool = Field(False, description="Bypass prompt template")
    keep_alive: str | int | None = Field("5m", description="Model keep-alive duration")


class OllamaChatRequest(BaseModel):
    """Request model for Ollama chat endpoint."""

    model: str = Field(..., description="Model name to use")
    messages: list[OllamaChatMessage] = Field(
        ..., min_length=1, description="Chat messages"
    )
    format: Literal["json"] | None = Field(None, description="Response format")
    options: OllamaOptions | None = Field(None, description="Model options")
    template: str | None = Field(None, description="Prompt template")
    stream: bool = Field(True, description="Stream response")
    keep_alive: str | int | None = Field("5m", description="Model keep-alive duration")
    tools: list[dict[str, Any]] | None = Field(None, description="Available tools")


class OllamaShowRequest(BaseModel):
    """Request model for showing model information."""

    # Support both 'name' (original) and 'model' (Ollama SDK) fields
    name: str | None = Field(None, description="Model name to show")
    model: str | None = Field(None, description="Model name (Ollama SDK field)")
    verbose: bool = Field(False, description="Show verbose information")

    @model_validator(mode="after")
    def validate_model_name(self) -> Self:
        """Ensure we have either 'name' or 'model' field."""
        if not self.name and not self.model:
            raise ValueError("Either 'name' or 'model' field is required")
        # If model is provided but not name, copy it to name for backwards compatibility
        if self.model and not self.name:
            self.name = self.model
        # Vice versa
        if self.name and not self.model:
            self.model = self.name
        return self
