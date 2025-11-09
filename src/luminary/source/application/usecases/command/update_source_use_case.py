from luminary.source.application.interfaces.policies.source_access_policy import (
    ISourceAccessPolicy,
)
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.application.interfaces.usecases.command.update_source_use_case import (
    IUpdateSourceUseCase,
    UpdateSourceCommand,
)


class UpdateSourceUseCase(IUpdateSourceUseCase):
    def __init__(
        self,
        repository: ISourceRepository,
        access_policy: ISourceAccessPolicy,
    ) -> None:
        self.repository = repository
        self.access_policy = access_policy

    async def execute(self, command: UpdateSourceCommand) -> None:
        source = await self.repository.get_by_id(command.source_id)
        self.access_policy.assert_is_allowed(command.user_id, source)

        if source.title_matches(command.title):
            return None

        source.update_title(command.title)
        await self.repository.save(source)
