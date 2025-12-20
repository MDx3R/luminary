from common.application.exceptions import ApplicationError


class EmbeddingError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("embedding failed")
