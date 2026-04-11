from common.domain.interfaces.clock import IClock
from common.domain.value_objects.id import UserId

from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.update_editor_content_use_case import (
    IUpdateEditorContentUseCase,
    UpdateEditorContentCommand,
)
from luminary.folder.domain.value_objects.folder_id import FolderId


class UpdateEditorContentUseCase(IUpdateEditorContentUseCase):
    def __init__(
        self,
        repository: IFolderRepository,
        access_policy: IFolderAccessPolicy,
        clock: IClock,
    ) -> None:
        self.repository = repository
        self.access_policy = access_policy
        self.clock = clock

    async def execute(self, command: UpdateEditorContentCommand) -> None:
        folder = await self.repository.get_by_id(FolderId(command.folder_id))
        self.access_policy.assert_is_allowed(UserId(command.user_id), folder)

        if folder.editor_text_matches(command.text):
            return

        folder.update_editor_content(command.text, self.clock.now())
        await self.repository.save(folder)
