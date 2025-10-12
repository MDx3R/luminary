from uuid import UUID


class ApplicationError(Exception):
    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.cause = cause

    def __str__(self) -> str:
        base = self.message or self.__class__.__name__
        if self.__cause__:
            return f"{base} (caused by {self.__cause__.__class__.__name__}: {self.__cause__})"
        return base


class NotFoundError(ApplicationError):
    def __init__(self, entity_id: UUID | str) -> None:
        super().__init__(f"Not found {entity_id}")
        self.entity_id = entity_id


class RepositoryError(ApplicationError): ...


class OptimisticLockError(RepositoryError):
    def __init__(self, message: str = "Concurrent update"):
        super().__init__(message)


class DuplicateEntryError(RepositoryError):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"Duplicate entry for field '{field}': {value} already exists")
