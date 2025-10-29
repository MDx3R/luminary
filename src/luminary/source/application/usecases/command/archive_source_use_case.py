from luminary.source.application.interfaces.policies.source_access_policy import (
    ISourceAccessPolicy,
)
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.application.interfaces.usecases.command.archive_source_use_case import (
    ArchiveSourceCommand,
    IArchiveSourceUseCase,
)


class ArchiveSourceUseCase(IArchiveSourceUseCase):
    def __init__(
        self,
        source_repository: ISourceRepository,
        access_policy: ISourceAccessPolicy,
    ) -> None:
        self.source_repository = source_repository
        self.access_policy = access_policy

    async def execute(self, command: ArchiveSourceCommand) -> None:
        source = await self.source_repository.get_by_id(command.source_id)
        self.access_policy.assert_is_allowed(command.user_id, source)
        await self.source_repository.delete(command.source_id)
