from datetime import datetime, UTC
from uuid import UUID, uuid4

from common.domain.value_objects.datetime import DateTime
from common.domain.value_objects.id import UserId
from luminary.assistant.domain.entity.assisnant import AssistantId
from luminary.folder.domain.entity.folder import FolderInfo, Folder, FolderId


def make_folder(
        *,
        folder_id: UUID | None = None,
        owner_id: UUID | None = None,
        info: FolderInfo | None = None,
        assistant_id: UUID | None = None,
        created_at: DateTime | None = None,
) -> Folder:
    folder_id = folder_id or uuid4()
    owner_id = owner_id or uuid4()
    info = info or FolderInfo("Test Folder Name", "Test Folder Info")
    assistant_id = assistant_id or uuid4()

    return Folder(
        id=FolderId(folder_id),
        owner_id=UserId(owner_id),
        info=info,
        assistant_id=AssistantId(assistant_id),
        created_at=created_at or DateTime(datetime.now(UTC))
    )


