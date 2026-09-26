from common.domain.value_objects.id import UserId

from luminary.source.application.interfaces.policies.source_access_policy import (
    ISourceAccessPolicy,
)
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.application.interfaces.usecases.command.delete_source_use_case import (
    DeleteSourceCommand,
    IDeleteSourceUseCase,
)
from luminary.source.domain.entity.source import SourceId


class DeleteSourceUseCase(IDeleteSourceUseCase):
    def __init__(
        self, repository: ISourceRepository, access_policy: ISourceAccessPolicy
    ) -> None:
        self.repository = repository
        self.access_policy = access_policy

    async def execute(self, command: DeleteSourceCommand) -> None:
        source = await self.repository.get_by_id(SourceId(command.source_id))
        self.access_policy.assert_is_allowed(UserId(command.user_id), source)

        source.delete()
        await self.repository.save(source)
