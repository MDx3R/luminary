from common.application.value_objects.descriptor import IdentityDescriptor
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.user.application.dtos.profile import ExternalProfile
from luminary.user.application.interfaces.resolve_user_use_case import (
    IResolveUserUseCase,
)
from luminary.user.application.interfaces.user_repository import IUserRepository


class ResolveUserUseCase(IResolveUserUseCase):
    def __init__(
        self,
        user_repository: IUserRepository,
        uuid_generator: IUUIDGenerator,
    ) -> None:
        self.user_repository = user_repository
        self.uuid_generator = uuid_generator

    async def execute(
        self, profile: ExternalProfile, username: str
    ) -> IdentityDescriptor:
        user = await self.user_repository.get_by_subject(profile.subject)
        if user is None or (user.name, user.email) != (profile.name, profile.email):
            user = await self.user_repository.upsert(
                self.uuid_generator.create(), profile
            )
        return IdentityDescriptor(user.id, username, user.name, user.email)
