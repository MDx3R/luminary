from uuid import UUID

from common.domain.interfaces.clock import IClock
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.file.domain.entity.file import File
from luminary.file.domain.interfaces.file_factory import IFileFactory


class FileFactory(IFileFactory):
    def __init__(self, clock: IClock, uuid_generator: IUUIDGenerator) -> None:
        self.clock = clock
        self.uuid_generator = uuid_generator

    def create(
        self,
        user_id: UUID,
        filename: str,
        extension: str,
        mime: str,
    ) -> File:
        return File.create(
            file_id=self.uuid_generator.create(),
            user_id=user_id,
            filename=filename,
            extension=extension,
            mime=mime,
            created_at=self.clock.now(),
        )
