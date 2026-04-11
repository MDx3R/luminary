"""Application entry point."""

from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from bootstrap.config import AppConfig
from bootstrap.utils import log_config
from common.infrastructure.database.sqlalchemy.database import Database
from common.infrastructure.di.container.common import CommonContainer
from common.infrastructure.logger.logging.logger_factory import LoggerFactory
from common.infrastructure.queues.faststream.event_bus import FastStreamRabbitMQEventBus
from common.infrastructure.queues.faststream.utils import create_rabbit
from common.infrastructure.storage.minio.client import MinioStorage
from common.infrastructure.storage.qdrant.client import QdrantStore
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from faststream.rabbit import RabbitRoute, RabbitRouter
from idp.auth.application.interfaces.usecases.command.login_use_case import (
    ILoginUseCase,
)
from idp.auth.application.interfaces.usecases.command.logout_use_case import (
    ILogoutUseCase,
)
from idp.auth.application.interfaces.usecases.command.refresh_token_use_case import (
    IRefreshTokenUseCase,
)
from idp.auth.infrastructure.di.container.container import AuthContainer, TokenContainer
from idp.auth.presentation.http.fastapi.controllers import auth_router
from idp.identity.application.interfaces.services.token_intospector import (
    ITokenIntrospector,
)
from idp.identity.application.interfaces.usecases.command.create_identity_use_case import (
    ICreateIdentityUseCase,
)
from idp.identity.infrastructure.di.container.container import IdentityContainer
from idp.identity.presentation.http.fastapi.controllers import identity_router
from llama_index.core import Settings, VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from luminary_files.application.interfaces.services.file_service import IFileService
from luminary_files.infrastructure.di.container import FileContainer

from luminary.assistant.application.interfaces.usecases.command.create_assistant_use_case import (
    ICreateAssistantUseCase,
)
from luminary.assistant.application.interfaces.usecases.command.delete_assistant_use_case import (
    IDeleteAssistantUseCase,
)
from luminary.assistant.application.interfaces.usecases.command.update_assistant_info_use_case import (
    IUpdateAssistantInfoUseCase,
)
from luminary.assistant.application.interfaces.usecases.command.update_assistant_instructions_use_case import (
    IUpdateAssistantInstructionsUseCase,
)
from luminary.assistant.application.interfaces.usecases.query.get_assistant_use_case import (
    IGetAssistantByIdUseCase,
)
from luminary.assistant.application.interfaces.usecases.query.list_assistants_use_case import (
    IListAssistantsUseCase,
)
from luminary.assistant.domain.events.events import AssistantDeletedEvent
from luminary.assistant.infrastructure.di.container import AssistantContainer
from luminary.assistant.presentation.http.fastapi.controllers import (
    command_router as assistant_command_router,
    query_router as assistant_query_router,
)
from luminary.chat.application.interfaces.usecases.command.add_source_to_chat_use_case import (
    IAddSourceToChatUseCase,
)
from luminary.chat.application.interfaces.usecases.command.cancel_message_use_case import (
    ICancelMessageUseCase,
)
from luminary.chat.application.interfaces.usecases.command.change_chat_assistant_use_case import (
    IChangeChatAssistantUseCase,
)
from luminary.chat.application.interfaces.usecases.command.create_chat_use_case import (
    ICreateChatUseCase,
)
from luminary.chat.application.interfaces.usecases.command.delete_chat_use_case import (
    IDeleteChatUseCase,
)
from luminary.chat.application.interfaces.usecases.command.get_message_response_use_case import (
    IGetStreamingMessageResponseUseCase,
)
from luminary.chat.application.interfaces.usecases.command.remove_chat_assistant_use_case import (
    IRemoveChatAssistantUseCase,
)
from luminary.chat.application.interfaces.usecases.command.remove_source_from_chat_use_case import (
    IRemoveSourceFromChatUseCase,
)
from luminary.chat.application.interfaces.usecases.command.send_message_use_case import (
    ISendMessageUseCase,
)
from luminary.chat.application.interfaces.usecases.command.update_chat_name_use_case import (
    IUpdateChatNameUseCase,
)
from luminary.chat.application.interfaces.usecases.command.update_chat_settings_use_case import (
    IUpdateChatSettingsUseCase,
)
from luminary.chat.application.interfaces.usecases.query.get_chat_use_case import (
    IGetChatByIdUseCase,
)
from luminary.chat.application.interfaces.usecases.query.list_chat_messages_use_case import (
    IListChatMessagesUseCase,
)
from luminary.chat.application.interfaces.usecases.query.list_user_chats_use_case import (
    IListUserChatsUseCase,
)
from luminary.chat.domain.events.events import ChatDeletedEvent, ChatSourceRemovedEvent
from luminary.chat.infrastructure.di.container import ChatContainer
from luminary.chat.presentation.http.fastapi.controllers import (
    command_router as chat_command_router,
    query_router as chat_query_router,
)
from luminary.content.infrastructure.di.container import ContentContainer
from luminary.folder.application.interfaces.usecases.command.add_source_to_folder_use_case import (
    IAddSourceToFolderUseCase,
)
from luminary.folder.application.interfaces.usecases.command.change_folder_assistant_use_case import (
    IChangeFolderAssistantUseCase,
)
from luminary.folder.application.interfaces.usecases.command.create_folder_chat_use_case import (
    ICreateFolderChatUseCase,
)
from luminary.folder.application.interfaces.usecases.command.create_folder_use_case import (
    ICreateFolderUseCase,
)
from luminary.folder.application.interfaces.usecases.command.delete_folder_use_case import (
    IDeleteFolderUseCase,
)
from luminary.folder.application.interfaces.usecases.command.remove_chat_from_folder_use_case import (
    IRemoveChatFromFolderUseCase,
)
from luminary.folder.application.interfaces.usecases.command.remove_folder_assistant_use_case import (
    IRemoveFolderAssistantUseCase,
)
from luminary.folder.application.interfaces.usecases.command.remove_source_from_folder_use_case import (
    IRemoveSourceFromFolderUseCase,
)
from luminary.folder.application.interfaces.usecases.command.update_editor_content_use_case import (
    IUpdateEditorContentUseCase,
)
from luminary.folder.application.interfaces.usecases.command.update_folder_info_use_case import (
    IUpdateFolderInfoUseCase,
)
from luminary.folder.application.interfaces.usecases.query.get_folder_use_case import (
    IGetFolderByIdUseCase,
)
from luminary.folder.application.interfaces.usecases.query.list_user_folders_use_case import (
    IListUserFoldersUseCase,
)
from luminary.folder.domain.events.events import (
    FolderChatRemovedEvent,
    FolderSourceRemovedEvent,
)
from luminary.folder.infrastructure.di.container import FolderContainer
from luminary.folder.presentation.http.fastapi.controllers import (
    command_router as folder_command_router,
    query_router as folder_query_router,
)
from luminary.model.infrastructure.di.container import ModelContainer
from luminary.model.infrastructure.services.llama_index.client import (
    MappedOpenAI,
    MappedOpenAIEmbedding,
)
from luminary.source.application.interfaces.usecases.command.create_source_use_case import (
    ICreateFileSourceUseCase,
    ICreateLinkSourceUseCase,
    ICreatePageSourceUseCase,
)
from luminary.source.application.interfaces.usecases.command.delete_source_use_case import (
    IDeleteSourceUseCase,
)
from luminary.source.application.interfaces.usecases.command.update_source_use_case import (
    IUpdateSourceUseCase,
)
from luminary.source.application.interfaces.usecases.query.get_source_use_case import (
    IGetSourceByIdUseCase,
)
from luminary.source.application.interfaces.usecases.query.list_user_sources_use_case import (
    IListUserSourcesUseCase,
)
from luminary.source.domain.events.events import (
    SourceCreatedEvent,
    SourceDeletedEvent,
    SourceFetchedEvent,
)
from luminary.source.infrastructure.di.container import SourceContainer
from luminary.source.presentation.http.fastapi.controllers import (
    command_router as source_command_router,
    query_router as source_query_router,
)


FILES_BUCKET = "files"
CONTENT_BUCKET = "content"

FORBIDDEN_MIME_TYPES = [
    # Video
    "video/*",
    # Audio
    "audio/*",
    # Fonts
    "font/*",
    # Archives and compressed
    "application/zip",
    "application/x-tar",
    "application/gzip",
    "application/x-7z-compressed",
    "application/x-rar-compressed",
    "application/x-bzip2",
    "application/x-xz",
    # Executables and scripts
    "application/x-msdownload",
    "application/x-dosexec",
    "application/x-sh",
    # JavaScript & other code
    "*/javascript"
    # Installers and packages
    "application/x-apple-diskimage",
    "application/x-ms-installer",
    "application/x-deb",
    "application/x-rpm",
]


# Load configuration
config = AppConfig.load()

# Logger
logger = LoggerFactory.create(None, config.env, config.logger)
logger.info("logger initialized")

log_config(logger, config)


def create_source_routes(
    event_bus: FastStreamRabbitMQEventBus, container: SourceContainer
) -> Sequence[RabbitRoute]:
    return [
        event_bus.build_route(
            event_bus.prefix, SourceCreatedEvent, container.source_created_handler()
        ),
        event_bus.build_route(
            event_bus.prefix, SourceFetchedEvent, container.source_fetched_handler()
        ),
    ]


def create_folder_routes(
    event_bus: FastStreamRabbitMQEventBus, container: FolderContainer
) -> Sequence[RabbitRoute]:
    return [
        event_bus.build_route(
            event_bus.prefix,
            SourceDeletedEvent,
            container.source_deleted_handler(),
        ),
        event_bus.build_route(
            event_bus.prefix,
            FolderSourceRemovedEvent,
            container.source_removed_handler(),
        ),
        event_bus.build_route(
            event_bus.prefix, ChatDeletedEvent, container.chat_deleted_handler()
        ),
        event_bus.build_route(
            event_bus.prefix, FolderChatRemovedEvent, container.chat_removed_handler()
        ),
        event_bus.build_route(
            event_bus.prefix,
            FolderChatRemovedEvent,
            container.chat_removed_association_handler(),
        ),
        event_bus.build_route(
            event_bus.prefix,
            FolderChatRemovedEvent,
            container.chat_removed_association_handler(),
        ),
        event_bus.build_route(
            event_bus.prefix,
            AssistantDeletedEvent,
            container.assistant_deleted_handler(),
        ),
    ]


def create_chat_routes(
    event_bus: FastStreamRabbitMQEventBus, container: ChatContainer
) -> Sequence[RabbitRoute]:
    return [
        event_bus.build_route(
            event_bus.prefix,
            SourceDeletedEvent,
            container.source_deleted_handler(),
        ),
        event_bus.build_route(
            event_bus.prefix,
            ChatSourceRemovedEvent,
            container.source_removed_handler(),
        ),
        event_bus.build_route(
            event_bus.prefix,
            AssistantDeletedEvent,
            container.assistant_deleted_handler(),
        ),
    ]


def main() -> FastAPI:  # noqa: PLR0915
    """Initialize and bootstrap the application.

    Returns:
        Configured App instance.

    """
    # Database
    logger.info("initializing database...")
    database = Database.create(config.db, logger)
    logger.info("database initialized")

    # MinIO
    logger.info("initializing MinIO storage...")
    storage = MinioStorage.create(config.s3)
    logger.info("MinIO storage initialized")

    # RabbitMQ
    logger.info("initializing broker...")
    broker = create_rabbit(config.rabbit)
    logger.info("broker initialized")

    # LLM
    llm = MappedOpenAI(
        model=config.llm.model,
        api_key=config.llm.api_key,
        api_base=config.llm.base_url,
        temperature=0.3,
    )
    MappedOpenAI.override(config.llm.model, config.llm.provider_model)
    logger.info("llm initialized")

    # Embedding Model
    MappedOpenAIEmbedding.override(
        config.llm.embed_model, config.llm.provider_embed_model
    )
    embed_model = MappedOpenAIEmbedding(
        model=config.llm.embed_model,
        api_key=config.llm.api_key,
        api_base=config.llm.base_url,
    )
    logger.info("embedding model initialized")

    Settings.llm, Settings.embed_model = llm, embed_model

    # Vector store
    logger.info("initializing vector store...")

    qdrant_store = QdrantStore.create(config.qdrant)
    vector_store = QdrantVectorStore(
        collection_name=config.qdrant.collection_name, aclient=qdrant_store.get_client()
    )
    vector_store_index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store, embed_model=embed_model
    )

    logger.info("vector store initialized")

    # Create FastAPI server
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
        logger.info("application ready to accept requests")
        await broker.start()
        await storage.ensure_bucket()
        await storage.ensure_bucket(FILES_BUCKET)
        await storage.ensure_bucket(CONTENT_BUCKET)
        await qdrant_store.ensure_collection()

        yield
        logger.info("application shutdown begins")
        await broker.stop()
        await database.shutdown()
        await storage.shutdown()
        await qdrant_store.shutdown()

    server = FastAPI(lifespan=lifespan)

    # Bootstrap common container with config and database
    common_container = CommonContainer(
        config=config,
        logger=logger,
        database=database,
        storage=storage,
        broker=broker,
        queue_name=config.rabbit.queue_name,
    )

    uuid_generator = common_container.uuid_generator
    query_executor = common_container.query_executor
    clock = common_container.clock
    unit_of_work = common_container.unit_of_work
    event_bus = common_container.event_bus

    identity_container = IdentityContainer(
        uuid_generator=uuid_generator,
        query_executor=query_executor,
        token_introspector=None,  # NOTE: Need to be overriden later
    )

    token_container = TokenContainer(
        auth_config=config.auth,
        clock=clock,
        uuid_generator=uuid_generator,
        token_generator=common_container.token_generator,
        query_executor=query_executor,
        identity_repository=identity_container.identity_repository,
    )

    identity_container.token_introspector.override(  # pyright: ignore[reportUnknownMemberType]
        token_container.token_introspector
    )

    auth_container = AuthContainer(
        identity_service=identity_container.identity_service,
        token_issuer=token_container.token_issuer,
        token_revoker=token_container.token_revoker,
        token_refresher=token_container.token_refresher,
    )

    file_container = FileContainer(
        bucket_name=FILES_BUCKET,
        clock=clock,
        uuid_generator=uuid_generator,
        query_executor=query_executor,
        storage=storage.get_client(),
        blacklisted_mime_types=FORBIDDEN_MIME_TYPES,
    )

    file_type_introspector = file_container.file_type_introspector
    file_service = file_container.file_service

    content_container = ContentContainer(
        bucket_name=CONTENT_BUCKET,
        clock=clock,
        uuid_generator=uuid_generator,
        query_executor=query_executor,
        storage=storage.get_client(),
        file_content_extractor=None,  # NOTE: Has to be overriden later
    )

    content_service = content_container.content_service

    model_container = ModelContainer(
        vector_store_index=vector_store_index,
        embed_model=embed_model,
        llm=llm,
        file_type_introspector=file_type_introspector,
    )

    content_container.file_content_extractor.override(model_container.content_extractor)

    embedding_service = model_container.embedding_service

    source_container = SourceContainer(
        clock=clock,
        uuid_generator=uuid_generator,
        query_executor=query_executor,
        unit_of_work=unit_of_work,
        event_bus=event_bus,
        file_service=file_service,
        content_service=content_service,
        embedding_service=embedding_service,
    )

    assistant_container = AssistantContainer(
        clock=clock,
        uuid_generator=uuid_generator,
        query_executor=query_executor,
        unit_of_work=unit_of_work,
        event_bus=event_bus,
    )

    chat_container = ChatContainer(
        clock=clock,
        uuid_generator=uuid_generator,
        query_executor=query_executor,
        unit_of_work=unit_of_work,
        event_bus=event_bus,
        inference_engine=model_container.inference_engine,
        assistant_repository=assistant_container.event_bus_assistant_repository,
    )

    folder_container = FolderContainer(
        clock=clock,
        uuid_generator=uuid_generator,
        query_executor=query_executor,
        unit_of_work=unit_of_work,
        event_bus=event_bus,
        chat_factory=chat_container.chat_factory,
        chat_repository=chat_container.event_bus_chat_repository,
    )
    chat_container.folder_repository.override(
        folder_container.event_bus_folder_repository
    )

    rabbit_router = RabbitRouter(
        handlers=[
            *create_source_routes(event_bus(), source_container),
            *create_folder_routes(event_bus(), folder_container),
            *create_chat_routes(event_bus(), chat_container),
        ]
    )
    broker.include_router(rabbit_router)

    # Register routes
    server.dependency_overrides[IFileService] = lambda: file_container.file_service()
    server.dependency_overrides[ICreateFileSourceUseCase] = (
        lambda: source_container.create_file_source_use_case()
    )
    server.dependency_overrides[ICreatePageSourceUseCase] = (
        lambda: source_container.create_page_source_use_case()
    )
    server.dependency_overrides[ICreateLinkSourceUseCase] = (
        lambda: source_container.create_link_source_use_case()
    )
    server.dependency_overrides[IGetSourceByIdUseCase] = (
        lambda: source_container.get_source_by_id_use_case()
    )
    server.dependency_overrides[IListUserSourcesUseCase] = (
        lambda: source_container.list_user_sources_use_case()
    )
    server.dependency_overrides[IUpdateSourceUseCase] = (
        lambda: source_container.update_source_use_case()
    )
    server.dependency_overrides[IDeleteSourceUseCase] = (
        lambda: source_container.delete_source_use_case()
    )

    server.dependency_overrides[ICreateAssistantUseCase] = (
        lambda: assistant_container.create_assistant_use_case()
    )
    server.dependency_overrides[IUpdateAssistantInfoUseCase] = (
        lambda: assistant_container.update_assistant_info_use_case()
    )
    server.dependency_overrides[IUpdateAssistantInstructionsUseCase] = (
        lambda: assistant_container.update_assistant_instructions_use_case()
    )
    server.dependency_overrides[IDeleteAssistantUseCase] = (
        lambda: assistant_container.delete_assistant_use_case()
    )
    server.dependency_overrides[IGetAssistantByIdUseCase] = (
        lambda: assistant_container.get_assistant_by_id_use_case()
    )
    server.dependency_overrides[IListAssistantsUseCase] = (
        lambda: assistant_container.list_assistants_use_case()
    )

    server.dependency_overrides[ICreateChatUseCase] = (
        lambda: chat_container.create_chat_use_case()
    )
    server.dependency_overrides[IUpdateChatNameUseCase] = (
        lambda: chat_container.update_chat_name_use_case()
    )
    server.dependency_overrides[IUpdateChatSettingsUseCase] = (
        lambda: chat_container.update_chat_settings_use_case()
    )
    server.dependency_overrides[IChangeChatAssistantUseCase] = (
        lambda: chat_container.change_chat_assistant_use_case()
    )
    server.dependency_overrides[IRemoveChatAssistantUseCase] = (
        lambda: chat_container.remove_chat_assistant_use_case()
    )
    server.dependency_overrides[IAddSourceToChatUseCase] = (
        lambda: chat_container.add_source_to_chat_use_case()
    )
    server.dependency_overrides[IRemoveSourceFromChatUseCase] = (
        lambda: chat_container.remove_source_from_chat_use_case()
    )
    server.dependency_overrides[IDeleteChatUseCase] = (
        lambda: chat_container.delete_chat_use_case()
    )
    server.dependency_overrides[ISendMessageUseCase] = (
        lambda: chat_container.send_message_use_case()
    )
    server.dependency_overrides[ICancelMessageUseCase] = (
        lambda: chat_container.cancel_message_use_case()
    )
    server.dependency_overrides[IGetStreamingMessageResponseUseCase] = (
        lambda: chat_container.get_streaming_message_response_use_case()
    )
    server.dependency_overrides[IGetChatByIdUseCase] = (
        lambda: chat_container.get_chat_by_id_use_case()
    )
    server.dependency_overrides[IListUserChatsUseCase] = (
        lambda: chat_container.list_user_chats_use_case()
    )
    server.dependency_overrides[IListChatMessagesUseCase] = (
        lambda: chat_container.list_chat_messages_use_case()
    )

    server.dependency_overrides[ICreateFolderUseCase] = (
        lambda: folder_container.create_folder_use_case()
    )
    server.dependency_overrides[IUpdateFolderInfoUseCase] = (
        lambda: folder_container.update_folder_info_use_case()
    )
    server.dependency_overrides[IDeleteFolderUseCase] = (
        lambda: folder_container.delete_folder_use_case()
    )
    server.dependency_overrides[IChangeFolderAssistantUseCase] = (
        lambda: folder_container.change_folder_assistant_use_case()
    )
    server.dependency_overrides[IRemoveFolderAssistantUseCase] = (
        lambda: folder_container.remove_folder_assistant_use_case()
    )
    server.dependency_overrides[IAddSourceToFolderUseCase] = (
        lambda: folder_container.add_source_to_folder_use_case()
    )
    server.dependency_overrides[IRemoveSourceFromFolderUseCase] = (
        lambda: folder_container.remove_source_from_folder_use_case()
    )
    server.dependency_overrides[ICreateFolderChatUseCase] = (
        lambda: folder_container.create_folder_chat_use_case()
    )
    server.dependency_overrides[IRemoveChatFromFolderUseCase] = (
        lambda: folder_container.remove_chat_from_folder_use_case()
    )
    server.dependency_overrides[IUpdateEditorContentUseCase] = (
        lambda: folder_container.update_editor_content_use_case()
    )
    server.dependency_overrides[IGetFolderByIdUseCase] = (
        lambda: folder_container.get_folder_by_id_use_case()
    )
    server.dependency_overrides[IListUserFoldersUseCase] = (
        lambda: folder_container.list_user_folders_use_case()
    )

    server.dependency_overrides[ILoginUseCase] = lambda: auth_container.login_use_case()
    server.dependency_overrides[ILogoutUseCase] = (
        lambda: auth_container.logout_use_case()
    )
    server.dependency_overrides[IRefreshTokenUseCase] = (
        lambda: auth_container.refresh_token_use_case()
    )

    server.dependency_overrides[ICreateIdentityUseCase] = (
        lambda: identity_container.create_identity_use_case()
    )
    server.dependency_overrides[ITokenIntrospector] = (
        lambda: identity_container.token_introspector()
    )

    server.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    router = APIRouter()

    server.include_router(identity_router, prefix="/users", tags=["users"])
    server.include_router(auth_router, prefix="/auth", tags=["auth"])

    router.include_router(source_command_router, prefix="/sources", tags=["sources"])
    router.include_router(source_query_router, prefix="/sources", tags=["sources"])
    router.include_router(
        assistant_command_router, prefix="/assistants", tags=["assistants"]
    )
    router.include_router(
        assistant_query_router, prefix="/assistants", tags=["assistants"]
    )
    router.include_router(chat_command_router, prefix="/chats", tags=["chats"])
    router.include_router(chat_query_router, prefix="/chats", tags=["chats"])
    router.include_router(folder_command_router, prefix="/folders", tags=["folders"])
    router.include_router(folder_query_router, prefix="/folders", tags=["folders"])

    server.include_router(router, prefix="/api/v1")

    return server


app = main()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
