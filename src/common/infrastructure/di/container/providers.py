from common.infrastructure.database.sqlalchemy.database import Database
from common.infrastructure.database.sqlalchemy.session_factory import (
    ISessionFactory,
    MakerSessionFactory,
)


def provide_maker_session_factory(database: Database) -> ISessionFactory:
    return MakerSessionFactory(database.get_session_maker())
