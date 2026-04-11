from common.domain.value_objects.id import UserId

from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.application.interfaces.usecases.command.remove_chat_from_folder_use_case import (
    IRemoveChatFromFolderUseCase,
    RemoveChatFromFolderCommand,
)
from luminary.folder.domain.value_objects.folder_id import FolderId


class RemoveChatFromFolderUseCase(IRemoveChatFromFolderUseCase):
    def __init__(
        self,
        repository: IFolderRepository,
        access_policy: IFolderAccessPolicy,
    ) -> None:
        self.repository = repository
        self.access_policy = access_policy

    async def execute(self, command: RemoveChatFromFolderCommand) -> None:
        folder = await self.repository.get_by_id(FolderId(command.folder_id))
        self.access_policy.assert_is_allowed(UserId(command.user_id), folder)

        if not folder.has_chat(ChatId(command.chat_id)):
            return

        folder.remove_chat(ChatId(command.chat_id))
        await self.repository.save(folder)
