from uuid import UUID, uuid4
from datetime import UTC, datetime
from unittest.mock import Mock

from common.domain.value_objects.datetime import DateTime
from luminary.folder.domain.entity.folder import Folder, FolderInfo

def make_folder(
    *,
    folder_id: UUID | None = None,
    user_id: UUID | None = None,
    name: str = "Test Folder",
    description: str = "Test Description",
    model_id: UUID | None = None,
    assistant_id: UUID | None = None,
) -> Folder:
    return Folder(
        folder_id=folder_id or uuid4(),
        user_id=user_id or uuid4(),
        info=FolderInfo(name=name, description=description),
        model_id=model_id or uuid4(),
        assistant_id=assistant_id or uuid4(),
        created_at=Mock(spec=DateTime),  # In real test use DateTime(datetime.now(UTC))
        _chats=set(),
        _sources=set()
    )