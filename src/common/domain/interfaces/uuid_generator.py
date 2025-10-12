from abc import ABC, abstractmethod
from uuid import UUID


class IUUIDGenerator(ABC):
    """Interface for UUID generator classes.

    This abstract base class defines the contract for UUID generator implementations.
    Implementations must provide a `create` method that returns a new UUID instance.
    """

    @abstractmethod
    def create(self) -> UUID: ...
