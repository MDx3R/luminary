from abc import ABC, abstractmethod


class ITokenGenerator(ABC):
    @abstractmethod
    def hex(self, length: int) -> str: ...

    @abstractmethod
    def numeric(self, length: int) -> str: ...

    @abstractmethod
    def urlsafe(self, length: int) -> str: ...

    @abstractmethod
    def secure(self, length: int = 64) -> str: ...
