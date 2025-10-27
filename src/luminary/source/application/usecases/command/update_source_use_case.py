from luminary.source.application.interfaces.policies.source_access_policy import (
    ISourceAccessPolicy,
)
from luminary.source.application.interfaces.repositories.source_repository import (
    ISourceRepository,
)
from luminary.source.application.interfaces.usecases.command.create_source_use_case import (
    SourceDTO,
)
from luminary.source.application.interfaces.usecases.command.update_source_use_case import (
    IUpdateSourceUseCase,
    UpdateSourceCommand,
)
from luminary.source.domain.entity.source import Source


class UpdateSourceUseCase(IUpdateSourceUseCase):
    def __init__(
        self,
        repository: ISourceRepository,
        access_policy: ISourceAccessPolicy,
    ) -> None:
        self.repository = repository
        self.access_policy = access_policy

    async def execute(self, command: UpdateSourceCommand) -> SourceDTO:
        source = await self.repository.get_by_id(command.source_id)
        self.access_policy.assert_is_allowed(command.user_id, source)

        updated_source = Source.create(
            source_id=source.source_id,
            user_id=source.user_id,
            name=command.name,
            created_at=source.created_at,
        )
        await self.repository.save(updated_source)
        return SourceDTO(
            source_id=updated_source.source_id,
            user_id=updated_source.user_id,
            name=updated_source.name,
            created_at=updated_source.created_at,
        )
