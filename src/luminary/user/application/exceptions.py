from common.application.exceptions import ApplicationError


class InvalidIdentityError(ApplicationError):
    def __init__(self, message: str = "Invalid identity") -> None:
        super().__init__(message)


class IdentityProviderUnavailableError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("Identity provider unavailable")
