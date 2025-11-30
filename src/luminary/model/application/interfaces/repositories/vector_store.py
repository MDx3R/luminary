from abc import ABC, abstractmethod


class IVectorStore(ABC):
    @abstractmethod
    async def save(self, content: str) -> None: ...
