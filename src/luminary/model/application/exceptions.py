from common.application.exceptions import ApplicationError


class EmbeddingError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("embedding failed")


class InferenceError(ApplicationError):
    """Raised when inference (RAG/LLM) fails after retries or due to timeout."""

    def __init__(
        self, message: str = "inference failed", *, cause: Exception | None = None
    ) -> None:
        super().__init__(message, cause=cause)
