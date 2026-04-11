"""Chat bounded context DI container."""

from typing import Any

from dependency_injector import containers, providers

from luminary.chat.application.handlers.assistant_deleted_handler import (
    ChatAssistantDeletedHandler,
)
from luminary.chat.application.handlers.source_deleted_handler import (
    ChatSourceDeletedHandler,
    ChatSourceRemovedHandler,
)
from luminary.chat.application.policies.chat_access_policy import (
    ChatAccessPolicy,
)
from luminary.chat.application.repositories.chat_repository import (
    EventBusChatRepository,
)
from luminary.chat.application.repositories.message_repository import (
    EventBusMessageRepository,
)
from luminary.chat.application.usecases.command.add_source_to_chat_use_case import (
    AddSourceToChatUseCase,
)
from luminary.chat.application.usecases.command.cancel_message_use_case import (
    CancelMessageUseCase,
)
from luminary.chat.application.usecases.command.change_chat_assistant_use_case import (
    ChangeChatAssistantUseCase,
)
from luminary.chat.application.usecases.command.create_chat_use_case import (
    CreateChatUseCase,
)
from luminary.chat.application.usecases.command.delete_chat_use_case import (
    DeleteChatUseCase,
)
from luminary.chat.application.usecases.command.get_message_response_use_case import (
    GetStreamingMessageResponseUseCase,
)
from luminary.chat.application.usecases.command.remove_chat_assistant_use_case import (
    RemoveChatAssistantUseCase,
)
from luminary.chat.application.usecases.command.remove_source_from_chat_use_case import (
    RemoveSourceFromChatUseCase,
)
from luminary.chat.application.usecases.command.send_message_use_case import (
    SendMessageUseCase,
)
from luminary.chat.application.usecases.command.update_chat_name_use_case import (
    UpdateChatNameUseCase,
)
from luminary.chat.application.usecases.command.update_chat_settings_use_case import (
    UpdateChatSettingsUseCase,
)
from luminary.chat.application.usecases.query.get_chat_use_case import (
    GetChatByIdUseCase,
)
from luminary.chat.application.usecases.query.list_chat_messages_use_case import (
    ListChatMessagesUseCase,
)
from luminary.chat.application.usecases.query.list_user_chats_use_case import (
    ListUserChatsUseCase,
)
from luminary.chat.domain.factories.chat_factory import ChatFactory
from luminary.chat.domain.factories.message_factory import MessageFactory
from luminary.chat.infrastructure.database.postgres.sqlalchemy.repositories.chat_read_repository import (
    ChatReadRepository,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.repositories.chat_repository import (
    ChatRepository,
)
from luminary.chat.infrastructure.database.postgres.sqlalchemy.repositories.message_repository import (
    MessageRepository,
)


class ChatContainer(containers.DeclarativeContainer):
    """Dependency injection container for chat bounded context."""

    clock: providers.Dependency[Any] = providers.Dependency()
    uuid_generator: providers.Dependency[Any] = providers.Dependency()
    query_executor: providers.Dependency[Any] = providers.Dependency()
    unit_of_work: providers.Dependency[Any] = providers.Dependency()
    event_bus: providers.Dependency[Any] = providers.Dependency()
    inference_engine: providers.Dependency[Any] = providers.Dependency()
    assistant_repository: providers.Dependency[Any] = providers.Dependency()
    folder_repository: providers.Dependency[Any] = providers.Dependency()

    chat_factory = providers.Singleton(
        ChatFactory, clock=clock, uuid_generator=uuid_generator
    )

    chat_repository = providers.Singleton(ChatRepository, query_executor)
    chat_read_repository = providers.Singleton(ChatReadRepository, query_executor)
    event_bus_chat_repository = providers.Singleton(
        EventBusChatRepository,
        uow=unit_of_work,
        event_bus=event_bus,
        repository=chat_repository,
    )

    message_factory = providers.Singleton(
        MessageFactory, clock=clock, uuid_generator=uuid_generator
    )
    message_repository = providers.Singleton(MessageRepository, query_executor)
    event_bus_message_repository = providers.Singleton(
        EventBusMessageRepository,
        uow=unit_of_work,
        event_bus=event_bus,
        repository=message_repository,
    )

    chat_access_policy = providers.Singleton(ChatAccessPolicy)

    send_message_use_case = providers.Singleton(
        SendMessageUseCase,
        chat_repository=event_bus_chat_repository,
        message_repository=event_bus_message_repository,
        message_factory=message_factory,
        access_policy=chat_access_policy,
    )
    get_streaming_message_response_use_case = providers.Singleton(
        GetStreamingMessageResponseUseCase,
        uow=unit_of_work,
        message_factory=message_factory,
        inference_engine=inference_engine,
        chat_repository=event_bus_chat_repository,
        assistant_repository=assistant_repository,
        folder_repository=folder_repository,
        message_reader=message_repository,
        message_repository=event_bus_message_repository,
        chat_access_policy=chat_access_policy,
    )
    cancel_message_use_case = providers.Singleton(
        CancelMessageUseCase,
        chat_repository=event_bus_chat_repository,
        message_repository=event_bus_message_repository,
        access_policy=chat_access_policy,
    )

    create_chat_use_case = providers.Singleton(
        CreateChatUseCase,
        chat_factory=chat_factory,
        chat_repository=event_bus_chat_repository,
    )
    update_chat_name_use_case = providers.Singleton(
        UpdateChatNameUseCase,
        repository=event_bus_chat_repository,
        access_policy=chat_access_policy,
    )
    update_chat_settings_use_case = providers.Singleton(
        UpdateChatSettingsUseCase,
        repository=event_bus_chat_repository,
        access_policy=chat_access_policy,
    )
    change_chat_assistant_use_case = providers.Singleton(
        ChangeChatAssistantUseCase,
        repository=event_bus_chat_repository,
        access_policy=chat_access_policy,
    )
    remove_chat_assistant_use_case = providers.Singleton(
        RemoveChatAssistantUseCase,
        repository=event_bus_chat_repository,
        access_policy=chat_access_policy,
    )
    add_source_to_chat_use_case = providers.Singleton(
        AddSourceToChatUseCase,
        repository=event_bus_chat_repository,
        access_policy=chat_access_policy,
    )
    remove_source_from_chat_use_case = providers.Singleton(
        RemoveSourceFromChatUseCase,
        repository=event_bus_chat_repository,
        access_policy=chat_access_policy,
    )
    delete_chat_use_case = providers.Singleton(
        DeleteChatUseCase,
        repository=event_bus_chat_repository,
        access_policy=chat_access_policy,
    )

    # Query use cases
    get_chat_by_id_use_case = providers.Singleton(
        GetChatByIdUseCase, read_repository=chat_read_repository
    )
    list_user_chats_use_case = providers.Singleton(
        ListUserChatsUseCase, read_repository=chat_read_repository
    )
    list_chat_messages_use_case = providers.Singleton(
        ListChatMessagesUseCase, read_repository=chat_read_repository
    )

    assistant_deleted_handler = providers.Singleton(
        ChatAssistantDeletedHandler, chat_repository=event_bus_chat_repository
    )

    source_deleted_handler = providers.Singleton(
        ChatSourceDeletedHandler, chat_repository=event_bus_chat_repository
    )
    source_removed_handler = providers.Singleton(
        ChatSourceRemovedHandler, chat_repository=event_bus_chat_repository
    )
