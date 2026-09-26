from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class ISessionFactory(ABC):
    @abstractmethod
    def create(self) -> AsyncSession: ...


MAKER = async_sessionmaker[AsyncSession]


class MakerSessionFactory(ISessionFactory):
    _maker: MAKER

    def __init__(self, maker: MAKER) -> None:
        self._maker = maker

    def create(self) -> AsyncSession:
        return self._maker()

    def set_maker(self, maker: MAKER) -> None:
        self._maker = maker
