"""Assistant bounded context DI container."""

from typing import Any

from dependency_injector import containers, providers

from luminary.assistant.application.policies.assistant_access_policy import (
    AssistantAccessPolicy,
)
from luminary.assistant.application.repositories.assistant_repository import (
    EventBusAssistantRepository,
)
from luminary.assistant.application.usecases.command.create_assistant_use_case import (
    CreateAssistantUseCase,
)
from luminary.assistant.application.usecases.command.delete_assistant_use_case import (
    DeleteAssistantUseCase,
)
from luminary.assistant.application.usecases.command.update_assistant_info_use_case import (
    UpdateAssistantInfoUseCase,
)
from luminary.assistant.application.usecases.command.update_assistant_instructions_use_case import (
    UpdateAssistantInstructionsUseCase,
)
from luminary.assistant.application.usecases.query.get_assistant_use_case import (
    GetAssistantByIdUseCase,
)
from luminary.assistant.application.usecases.query.list_assistants_use_case import (
    ListAssistantsUseCase,
)
from luminary.assistant.domain.factories.assistant_factory import AssistantFactory
from luminary.assistant.infrastructure.database.postgres.sqlalchemy.repositories.assistant_read_repository import (
    AssistantReadRepository,
)
from luminary.assistant.infrastructure.database.postgres.sqlalchemy.repositories.assistant_repository import (
    AssistantRepository,
)


class AssistantContainer(containers.DeclarativeContainer):
    """Dependency injection container for assistant bounded context."""

    clock: providers.Dependency[Any] = providers.Dependency()
    uuid_generator: providers.Dependency[Any] = providers.Dependency()
    query_executor: providers.Dependency[Any] = providers.Dependency()
    unit_of_work: providers.Dependency[Any] = providers.Dependency()
    event_bus: providers.Dependency[Any] = providers.Dependency()

    assistant_factory = providers.Singleton(
        AssistantFactory, clock=clock, uuid_generator=uuid_generator
    )

    assistant_repository = providers.Singleton(AssistantRepository, query_executor)
    assistant_read_repository = providers.Singleton(
        AssistantReadRepository, query_executor
    )
    event_bus_assistant_repository = providers.Singleton(
        EventBusAssistantRepository,
        uow=unit_of_work,
        event_bus=event_bus,
        repository=assistant_repository,
    )

    assistant_access_policy = providers.Singleton(AssistantAccessPolicy)

    create_assistant_use_case = providers.Singleton(
        CreateAssistantUseCase,
        assistant_factory=assistant_factory,
        assistant_repository=event_bus_assistant_repository,
    )
    update_assistant_info_use_case = providers.Singleton(
        UpdateAssistantInfoUseCase,
        repository=event_bus_assistant_repository,
        access_policy=assistant_access_policy,
    )
    update_assistant_instructions_use_case = providers.Singleton(
        UpdateAssistantInstructionsUseCase,
        repository=event_bus_assistant_repository,
        access_policy=assistant_access_policy,
    )
    delete_assistant_use_case = providers.Singleton(
        DeleteAssistantUseCase,
        repository=event_bus_assistant_repository,
        access_policy=assistant_access_policy,
    )

    # Query use cases
    get_assistant_by_id_use_case = providers.Singleton(
        GetAssistantByIdUseCase, read_repository=assistant_read_repository
    )
    list_assistants_use_case = providers.Singleton(
        ListAssistantsUseCase, read_repository=assistant_read_repository
    )
