from abc import ABC, abstractmethod
from typing import BinaryIO


class IFileContentExtractor(ABC):
    @abstractmethod
    async def extract(self, filename: str, data: BinaryIO) -> bytes: ...


class ILinkContentExtractor(ABC):
    @abstractmethod
    async def extract(self, url: str) -> bytes: ...
