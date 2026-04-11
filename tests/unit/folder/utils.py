from datetime import UTC, datetime
from uuid import UUID, uuid4

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId

from luminary.assistant.domain.entity.assistant import AssistantId
from luminary.folder.domain.entity.folder import Folder
from luminary.folder.domain.value_objects.folder_id import FolderId
from luminary.folder.domain.value_objects.folder_info import FolderInfo


def make_folder(  # noqa: PLR0913
    *,
    folder_id: UUID | None = None,
    owner_id: UUID | None = None,
    info: FolderInfo | None = None,
    assistant_id: UUID | None = None,
    created_at: DateTime | None = None,
    is_deleted: bool = False,
) -> Folder:
    folder_id = folder_id or uuid4()
    owner_id = owner_id or uuid4()
    info = info or FolderInfo("Test Folder Name", "Test Folder Info")

    return Folder(
        id=FolderId(folder_id),
        owner_id=UserId(owner_id),
        info=info,
        assistant_id=AssistantId(assistant_id) if assistant_id else None,
        created_at=created_at or DateTime(datetime.now(UTC)),
        is_deleted=is_deleted,
    )
