from datetime import timedelta
from typing import ClassVar

from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.id import UserId
from common.domain.value_objects.object_key import ObjectKey
from luminary_files.application.dtos.query.get_presigned_url_query import (
    GetPresignedUrlQuery,
)
from luminary_files.application.interfaces.repositories.file_repository import (
    IFileRepository,
)
from luminary_files.application.interfaces.repositories.file_storage import IFileStorage
from luminary_files.application.interfaces.usecases.query.get_presigned_url_use_case import (
    IGetFilePresignedUrlUseCase,
)


class GetFilePresignedUrlUseCase(IGetFilePresignedUrlUseCase):
    # TODO: Use init
    EXPIRATION_DELTA: ClassVar[timedelta] = timedelta(days=7)

    def __init__(
        self, file_repository: IFileRepository, file_storage: IFileStorage
    ) -> None:
        self.file_repository = file_repository
        self.file_storage = file_storage

    async def execute(self, query: GetPresignedUrlQuery) -> str:
        file = await self.file_repository.get_by_object_key(ObjectKey(query.object_key))

        if not file.is_owned_by(UserId(query.user_id)):
            raise AccessPolicyError(
                file.id, "file is accessable only to user who created it"
            )

        return await self.file_storage.get_presigned_get_url(
            file.object_key, self.EXPIRATION_DELTA
        )
