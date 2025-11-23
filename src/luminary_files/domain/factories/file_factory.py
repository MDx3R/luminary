from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator
from common.domain.value_objects.id import UserId
from luminary_files.domain.entity.file import File, FileId
from luminary_files.domain.exceptions import (
    InvalidMIMETypeError,
)
from luminary_files.domain.interfaces.extenstion_policy import (
    IMIMEPolicy,
)
from luminary_files.domain.interfaces.file_factory import IFileFactory


class FileFactory(IFileFactory):
    def __init__(
        self,
        clock: IClock,
        uuid_generator: IUUIDGenerator,
        mime_policy: IMIMEPolicy,
    ) -> None:
        self.clock = clock
        self.uuid_generator = uuid_generator
        self.mime_policy = mime_policy

    def create(self, user_id: UserId, filename: str, bucket: str, mime: str) -> File:
        if not self.mime_policy.is_allowed(mime):
            raise InvalidMIMETypeError(mime)

        return File.create(
            id=FileId(self.uuid_generator.create()),
            owner_id=user_id,
            filename=filename,
            bucket=bucket,
            mime=mime,
            uploaded_at=self.clock.now(),
        )
