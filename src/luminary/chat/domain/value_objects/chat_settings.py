from dataclasses import dataclass

from common.domain.exceptions import InvariantViolationError

from luminary.model.domain.entity.model import ModelId


@dataclass(frozen=True)
class ChatSettings:
    model_id: ModelId
    system_prompt: str
    max_context_messages: int

    def __post_init__(self) -> None:
        if not self.system_prompt.strip():
            raise InvariantViolationError("System prompt cannot be empty")
        if self.max_context_messages <= 0:
            raise InvariantViolationError(
                "Number of context messages cannot be non-positive"
            )
