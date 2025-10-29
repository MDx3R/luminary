from luminary.source.application.interfaces.policies.source_access_policy import (
    ISourceAccessPolicy,
)
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.application.interfaces.usecases.command.process_source_use_case import (
    IProcessSourceUseCase,
    ProcessSourceCommand,
)


class ProcessSourceUseCase(IProcessSourceUseCase):
    def __init__(
        self,
        source_repository: ISourceRepository,
        access_policy: ISourceAccessPolicy,
    ) -> None:
        self.source_repository = source_repository
        self.access_policy = access_policy

    async def execute(self, command: ProcessSourceCommand) -> None:
        source = await self.source_repository.get_by_id(command.source_id)
        self.access_policy.assert_is_allowed(command.user_id, source)
        pass
