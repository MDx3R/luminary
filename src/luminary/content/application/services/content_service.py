import io
from typing import BinaryIO, ClassVar
from uuid import UUID

from common.application.exceptions import AccessPolicyError
from common.domain.value_objects.id import UserId

from luminary.content.application.interfaces.repositories.content_repository import (
    IContentRepository,
)
from luminary.content.application.interfaces.repositories.content_storage import (
    IContentStorage,
)
from luminary.content.application.interfaces.services.content_extractor import (
    IFileContentExtractor,
)
from luminary.content.application.interfaces.services.content_service import (
    GetContentQuery,
    IContentService,
    ProcessFileCommand,
    ProcessLinkCommand,
)
from luminary.content.domain.entity.content import ContentId
from luminary.content.domain.interfaces.content_factory import IContentFactory


class ContentService(IContentService):
    CONTENT_MIME: ClassVar[str] = "text/plain"

    def __init__(
        self,
        bucket_name: str,
        content_factory: IContentFactory,
        file_content_extractor: IFileContentExtractor,
        content_repository: IContentRepository,
        content_storage: IContentStorage,
    ) -> None:
        self.bucket_name = bucket_name
        self.content_factory = content_factory
        self.file_content_extractor = file_content_extractor
        self.content_repository = content_repository
        self.content_storage = content_storage

    async def get_content(self, query: GetContentQuery) -> BinaryIO:
        content = await self.content_repository.get_by_id(ContentId(query.content_id))

        if not content.is_owned_by(UserId(query.user_id)):
            raise AccessPolicyError(
                content.id, "content is accessable only to user who created it"
            )

        return await self.content_storage.get(content.object_key)

    async def process_file(self, command: ProcessFileCommand) -> UUID:
        extracted_content = await self.file_content_extractor.extract(
            command.filename, command.data
        )

        content = self.content_factory.create(
            user_id=UserId(command.user_id),
            bucket=self.bucket_name,
            mime=self.CONTENT_MIME,
            size=len(extracted_content),
        )

        await self.content_storage.upload(
            content.object_key, content.mime, io.BytesIO(extracted_content)
        )

        await self.content_repository.add(content)

        return content.id.value

    async def process_link(self, command: ProcessLinkCommand) -> UUID:
        raise NotImplementedError
