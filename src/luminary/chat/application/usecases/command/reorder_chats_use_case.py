from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.id import UserId

from luminary.chat.application.interfaces.repositories.chat_repository import (
    IChatRepository,
)
from luminary.chat.application.interfaces.usecases.command.reorder_chats_use_case import (
    IReorderChatsUseCase,
    ReorderChatsCommand,
)
from luminary.chat.domain.value_objects.chat_id import ChatId
from luminary.folder.application.interfaces.policies.folder_access_policy import (
    IFolderAccessPolicy,
)
from luminary.folder.application.interfaces.repositories.folder_repository import (
    IFolderRepository,
)
from luminary.folder.domain.value_objects.folder_id import FolderId


class ReorderChatsUseCase(IReorderChatsUseCase):
    def __init__(
        self,
        chat_repository: IChatRepository,
        folder_repository: IFolderRepository,
        folder_access_policy: IFolderAccessPolicy,
    ) -> None:
        self.chat_repository = chat_repository
        self.folder_repository = folder_repository
        self.folder_access_policy = folder_access_policy

    async def execute(self, command: ReorderChatsCommand) -> None:
        owner_id = UserId(command.user_id)
        folder_id = FolderId.optional(command.folder_id)
        if folder_id is not None:
            folder = await self.folder_repository.get_by_id(folder_id)
            self.folder_access_policy.assert_is_allowed(owner_id, folder)

        requested = [ChatId(id) for id in command.chat_ids]
        current = await self.chat_repository.list_ids_by_location(owner_id, folder_id)
        if len(requested) != len(current) or set(requested) != set(current):
            raise InvariantViolationError(
                "chat_ids must contain every active chat in the location exactly once"
            )
        await self.chat_repository.set_order(owner_id, folder_id, requested)
