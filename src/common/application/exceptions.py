from typing import ClassVar

from common.domain.value_objects.id import EntityId


class ApplicationError(Exception):
    code: ClassVar[str] = "APPLICATION_ERROR"

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
    code = "NOT_FOUND"

    def __init__(self, entity_id: EntityId | str) -> None:
        super().__init__(f"Not found {entity_id}")
        self.entity_id = entity_id


class AccessPolicyError(ApplicationError):
    code = "ACCESS_DENIED"

    def __init__(self, entity_id: EntityId, message: str) -> None:
        super().__init__(f"{message}: {entity_id}")
        self.entity_id = entity_id


class RepositoryError(ApplicationError):
    code = "REPOSITORY_ERROR"


class OptimisticLockError(RepositoryError):
    code = "OPTIMISTIC_LOCK"

    def __init__(self, message: str = "Concurrent update"):
        super().__init__(message)


class DuplicateEntryError(RepositoryError):
    code = "DUPLICATE_ENTRY"

    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"Duplicate entry for field '{field}': {value} already exists")
