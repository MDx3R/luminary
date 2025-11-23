from abc import ABC, abstractmethod
from typing import BinaryIO


class IFileContentExtractor(ABC):
    @abstractmethod
    def extract(self, data: BinaryIO) -> bytes: ...


class ILinkContentExtractor(ABC):
    @abstractmethod
    def extract(self, url: str) -> bytes: ...
