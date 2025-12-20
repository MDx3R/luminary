from datetime import timedelta
from os import SEEK_END, SEEK_SET
from typing import BinaryIO, ClassVar
from uuid import UUID

from common.domain.value_objects.id import UserId
from common.domain.value_objects.object_key import ObjectKey
from luminary_files.application.dtos.query.get_presigned_url_query import (
    GetPresignedUrlQuery,
)
from luminary_files.application.interfaces.repositories.file_repository import (
    IFileRepository,
)
from luminary_files.application.interfaces.repositories.file_storage import IFileStorage
from luminary_files.application.interfaces.services.file_service import (
    GetFileQuery,
    IFileService,
    UploadFileCommand,
)
from luminary_files.application.interfaces.services.file_type_introspector import (
    IFileTypeIntrospector,
)
from luminary_files.domain.interfaces.file_factory import IFileFactory


class FileService(IFileService):
    BUCKET_NAME: ClassVar[str] = "files"
    EXPIRATION_DELTA: ClassVar[timedelta] = timedelta(days=7)

    def __init__(
        self,
        file_factory: IFileFactory,
        file_type_instorspector: IFileTypeIntrospector,
        file_repository: IFileRepository,
        file_storage: IFileStorage,
    ) -> None:
        self.file_factory = file_factory
        self.file_type_instorspector = file_type_instorspector
        self.file_repository = file_repository
        self.file_storage = file_storage

    async def upload_file(self, command: UploadFileCommand) -> UUID:
        content = command.content
        file_type = self.file_type_instorspector.extract(content)

        file = self.file_factory.create(
            user_id=UserId(command.user_id),
            filename=command.filename,
            bucket=self.BUCKET_NAME,
            mime=file_type.mime,
        )

        await self.file_storage.upload(file.object_key, file.meta.mime_type, content)

        # NOTE: File should be completely uploaded here
        # so we can safely extract file size
        size = content.seek(0, SEEK_END)
        file.specify_size(size)
        size = content.seek(0, SEEK_SET)
        await self.file_repository.add(file)

        return file.id.value

    async def get_file_presigned_url(self, query: GetPresignedUrlQuery) -> str:
        # TODO: Check user access
        return await self.file_storage.get_presigned_get_url(
            ObjectKey(query.object_key), self.EXPIRATION_DELTA
        )

    async def get_file(self, query: GetFileQuery) -> BinaryIO:
        return await self.file_storage.get(ObjectKey(query.object_key))
