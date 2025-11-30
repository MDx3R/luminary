from common.domain.exceptions import DomainError


class InvalidMIMETypeError(DomainError):
    def __init__(self, mime: str) -> None:
        super().__init__(f"Invalid file MIME type: {mime}")
