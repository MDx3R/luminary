from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class InferenceStreamChunk:
    content: str
    is_complete: bool
    message_id: UUID
    tokens: int | None = None
