from common.application.exceptions import ApplicationError


class InvalidFileTypeError(ApplicationError):
    def __init__(self, message: str = "File type cannot be determined"):
        super().__init__(message)
