from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from common.domain.value_objects.id import UserId


ENTITY = TypeVar("ENTITY", bound=object)


class IAccessPolicy(ABC, Generic[ENTITY]):
    @abstractmethod
    def is_allowed(self, user_id: UserId, entity: ENTITY) -> bool: ...

    @abstractmethod
    def assert_is_allowed(self, user_id: UserId, entity: ENTITY) -> None: ...
