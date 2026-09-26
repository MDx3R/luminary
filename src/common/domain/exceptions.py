class DomainError(Exception):
    """Exception raised for errors that occur within the domain logic."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvariantViolationError(DomainError): ...
