from abc import ABC, abstractmethod


class IMIMEPolicy(ABC):
    @abstractmethod
    def is_allowed(self, mime_type: str) -> bool: ...
