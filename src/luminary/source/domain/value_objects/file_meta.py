from dataclasses import dataclass

from common.domain.exceptions import InvariantViolationError


@dataclass(frozen=True)
class FileMeta:
    filename: str
    mime_type: str
    filesize: int
    checksum: str

    def __post_init__(self) -> None:
        if not self.filename.strip():
            raise InvariantViolationError("Filename cannot be empty")
        if not self.mime_type.strip():
            raise InvariantViolationError("MIME type cannot be empty")
        if not self.checksum.strip():
            raise InvariantViolationError("Checksum cannot be empty")
        if self.filesize <= 0:
            raise InvariantViolationError("File size must be positive number of bytes")
