from dataclasses import dataclass

from common.domain.exceptions import InvariantViolationError

from luminary.model.domain.entity.model import ModelId


@dataclass(frozen=True)
class ChatSettings:
    model_id: ModelId
    max_context_messages: int

    def __post_init__(self) -> None:
        if self.max_context_messages <= 0:
            raise InvariantViolationError(
                "Number of context messages cannot be non-positive"
            )
