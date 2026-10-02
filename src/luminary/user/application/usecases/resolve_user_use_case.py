from common.application.value_objects.descriptor import IdentityDescriptor
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from luminary.user.application.exceptions import InvalidIdentityError
from luminary.user.application.interfaces.profile_provider import IProfileProvider
from luminary.user.application.interfaces.resolve_user_use_case import (
    IResolveUserUseCase,
)
from luminary.user.application.interfaces.user_repository import IUserRepository


class ResolveUserUseCase(IResolveUserUseCase):
    def __init__(
        self,
        profile_provider: IProfileProvider,
        user_repository: IUserRepository,
        uuid_generator: IUUIDGenerator,
    ) -> None:
        self.profile_provider = profile_provider
        self.user_repository = user_repository
        self.uuid_generator = uuid_generator

    async def execute(
        self, subject: str, username: str, access_token: str
    ) -> IdentityDescriptor:
        profile = await self.profile_provider.get_profile(access_token)
        if profile.subject != subject:
            raise InvalidIdentityError("Identity does not match the access token")
        user = await self.user_repository.upsert(self.uuid_generator.create(), profile)
        return IdentityDescriptor(user.id, username, user.name, user.email)
