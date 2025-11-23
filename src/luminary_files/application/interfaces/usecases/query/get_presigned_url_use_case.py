from abc import ABC, abstractmethod

from luminary_files.application.dtos.query.get_presigned_url_query import (
    GetPresignedUrlQuery,
)


class IGetFilePresignedUrlUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetPresignedUrlQuery) -> str: ...
