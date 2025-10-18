from dataclasses import dataclass
from typing import Self
from uuid import UUID

from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.datetime import DateTime


@dataclass
class Source:
    source_id: UUID
    user_id: UUID
    filename: str
    extension: str
    mime: str
    edited_at: DateTime
    created_at: DateTime

    def __post_init__(self) -> None:
        if not self.filename.strip():
            raise InvariantViolationError("Sourcename cannot be empty")
        if not self.extension.strip():
            raise InvariantViolationError("Source extension cannot be empty")
        if not self.mime.strip():
            raise InvariantViolationError("Source MIME cannot be empty")

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        source_id: UUID,
        user_id: UUID,
        filename: str,
        extension: str,
        mime: str,
        created_at: DateTime,
    ) -> Self:
        return cls(
            source_id=source_id,
            user_id=user_id,
            filename=filename,
            extension=extension,
            mime=mime,
            edited_at=created_at,
            created_at=created_at,
        )
