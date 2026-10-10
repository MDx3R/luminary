from typing import ClassVar


class DomainError(Exception):
    """Exception raised for errors that occur within the domain logic."""

    code: ClassVar[str] = "DOMAIN_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvariantViolationError(DomainError):
    code = "INVARIANT_VIOLATION"
