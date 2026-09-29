from common.domain.value_objects.id import UserId

from luminary.chat.application.interfaces.policies.chat_access_policy import (
    IChatAccessPolicy,
)
from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.move_chat_use_case import (
    IMoveChatUseCase,
    MoveChatCommand,
)
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.domain.value_objects.folder_id import FolderId


class MoveChatUseCase(IMoveChatUseCase):
    def __init__(
        self,
        chat_repository: IChatRepository,
        folder_repository: IFolderRepository,
        chat_access_policy: IChatAccessPolicy,
        folder_access_policy: IFolderAccessPolicy,
    ) -> None:
        self.chat_repository = chat_repository
        self.folder_repository = folder_repository
        self.chat_access_policy = chat_access_policy
        self.folder_access_policy = folder_access_policy

    async def execute(self, command: MoveChatCommand) -> None:
        owner_id = UserId(command.user_id)
        chat = await self.chat_repository.get_by_id(ChatId(command.chat_id))
        self.chat_access_policy.assert_is_allowed(owner_id, chat)

        folder_id = FolderId.optional(command.folder_id)
        if folder_id is not None:
            folder = await self.folder_repository.get_by_id(folder_id)
            self.folder_access_policy.assert_is_allowed(owner_id, folder)

        if chat.folder_id == folder_id:
            return
        await self.chat_repository.move_to_folder(chat.id, folder_id)
