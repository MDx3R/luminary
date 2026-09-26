from dataclasses import dataclass

from common.domain.exceptions import InvariantViolationError


@dataclass(frozen=True)
class ChatInfo:
    name: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolationError("Chat name cannot be empty")
