from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from idp.identity.domain.value_objects.descriptor import IdentityDescriptor
from idp.identity.presentation.http.fastapi.auth import get_descriptor

from luminary.chat.application.interfaces.usecases.command.reorder_chats_use_case import (
    ReorderChatsCommand,
)
from luminary.chat.presentation.http.fastapi.controllers import (
    ChatCommandController,
    command_router as chat_router,
)
from luminary.folder.application.interfaces.usecases.command.reorder_folders_use_case import (
    ReorderFoldersCommand,
)
from luminary.folder.presentation.http.fastapi.controllers import (
    FolderCommandController,
    command_router as folder_router,
)


@pytest.fixture(params=["chat", "folder"])
def reorder_client(request):
    kind = request.param
    app = FastAPI()
    use_case = AsyncMock()
    descriptor = IdentityDescriptor(identity_id=uuid4(), username="test")
    controller = ChatCommandController if kind == "chat" else FolderCommandController
    router = chat_router if kind == "chat" else folder_router
    app.include_router(router, prefix=f"/api/v1/{kind}s")
    app.dependency_overrides[controller] = lambda: SimpleNamespace(
        **{f"reorder_{kind}s_use_case": use_case}
    )
    app.dependency_overrides[get_descriptor] = lambda: descriptor
    with TestClient(app) as client:
        yield client, kind, use_case, descriptor


@pytest.mark.parametrize("placement", ["start", "middle", "end"])
def test_reorder_http_passes_neighbours_to_use_case(reorder_client, placement) -> None:
    client, kind, use_case, descriptor = reorder_client
    entity_id = uuid4()
    previous = uuid4() if placement != "start" else None
    following = uuid4() if placement != "end" else None
    response = client.put(
        f"/api/v1/{kind}s/order",
        json={
            f"{kind}_id": str(entity_id),
            f"previous_{kind}_id": str(previous) if previous else None,
            f"next_{kind}_id": str(following) if following else None,
        },
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    command = ReorderChatsCommand if kind == "chat" else ReorderFoldersCommand
    use_case.execute.assert_awaited_once_with(
        command(descriptor.identity_id, entity_id, previous, following)
    )


@pytest.mark.parametrize(
    "payload",
    [{}, {"chat_ids": [], "folder_ids": []}, {"chat_id": "bad", "folder_id": "bad"}],
)
def test_reorder_http_rejects_invalid_or_old_payload(reorder_client, payload) -> None:
    client, kind, use_case, _ = reorder_client
    response = client.put(f"/api/v1/{kind}s/order", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    use_case.execute.assert_not_awaited()
