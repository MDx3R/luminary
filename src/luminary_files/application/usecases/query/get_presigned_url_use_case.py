from datetime import timedelta

from luminary_files.application.dtos.query.get_presigned_url_query import (
    GetPresignedUrlQuery,
)
from luminary_files.application.interfaces.repositories.file_storage import IFileStorage
from luminary_files.application.interfaces.usecases.query.get_presigned_url_use_case import (
    IGetPresignedUrlUseCase,
)
from luminary_files.domain.entity.file import ObjectKey


class GetPresignedUrlUseCase(IGetPresignedUrlUseCase):
    def __init__(self, file_storage: IFileStorage, expiration_delta: timedelta) -> None:
        self.file_storage = file_storage
        self.expiration_delta = expiration_delta

    async def execute(self, query: GetPresignedUrlQuery) -> str:
        return await self.file_storage.get_presigned_get_url(
            ObjectKey(query.object_key), self.expiration_delta
        )
