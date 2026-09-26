from dataclasses import dataclass

from common.domain.exceptions import InvariantViolationError


@dataclass(frozen=True)
class FolderInfo:
    name: str
    description: str | None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolationError("Folder name cannot be empty")
