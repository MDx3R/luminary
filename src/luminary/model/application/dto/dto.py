from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class OllamaChatMessage(BaseModel):
    """Chat message model for Ollama."""

    role: Literal["system", "user", "assistant", "tool"] = Field(
        ..., description="Message role"
    )
    content: str = Field(..., description="Message content")
    images: list[str] | None = Field(None, description="Base64 encoded images")
    tool_calls: list[dict[str, Any]] | None = Field(
        None, description="Tool calls made by assistant"
    )

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate message role."""
        valid_roles = {"system", "user", "assistant", "tool"}
        if v not in valid_roles:
            raise ValueError(f"Invalid role: {v}. Must be one of {valid_roles}")
        return v
