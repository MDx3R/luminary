from os import SEEK_END, SEEK_SET
from typing import BinaryIO
from uuid import UUID

from common.application.exceptions import NotFoundError
from common.domain.value_objects.id import UserId
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
from luminary_files.domain.entity.file import FileId
from luminary_files.domain.interfaces.file_factory import IFileFactory


class FileService(IFileService):
    def __init__(
        self,
        bucket_name: str,
        file_factory: IFileFactory,
        file_type_introspector: IFileTypeIntrospector,
        file_repository: IFileRepository,
        file_storage: IFileStorage,
    ) -> None:
        self.bucket_name = bucket_name
        self.file_factory = file_factory
        self.file_type_introspector = file_type_introspector
        self.file_repository = file_repository
        self.file_storage = file_storage

    async def upload_file(self, command: UploadFileCommand) -> UUID:
        content = command.content
        file_type = self.file_type_introspector.extract(content)

        file = self.file_factory.create(
            user_id=UserId(command.user_id),
            filename=command.filename,
            bucket=self.bucket_name,
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

    async def get_file(self, query: GetFileQuery) -> BinaryIO:
        file_id = FileId(query.file_id)
        file = await self.file_repository.get_by_id(file_id)

        if not file.is_owned_by(UserId(query.user_id)):
            raise NotFoundError(file_id)

        return await self.file_storage.get(file.object_key)
