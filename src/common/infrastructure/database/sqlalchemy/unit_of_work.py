import re
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from sqlite3 import IntegrityError
from types import TracebackType
from typing import Self

import psycopg2
import sqlalchemy.exc
import sqlalchemy.orm
from common.application.exceptions import (
    ApplicationError,
    DuplicateEntryError,
    OptimisticLockError,
    RepositoryError,
)
from common.application.interfaces.transactions.unit_of_work import IUnitOfWork
from common.infrastructure.database.sqlalchemy.session_factory import (
    ISessionFactory,
)
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class Transaction:
    session: AsyncSession
    nesting_level: int = 0

    def should_commit(self) -> bool:
        return self.nesting_level == 0

    def enter(self) -> None:
        self.nesting_level += 1

    def exit(self) -> None:
        self.nesting_level -= 1


class UnitOfWork(IUnitOfWork):
    def __init__(self, session_factory: ISessionFactory):
        self.session_factory = session_factory
        self._current_transaction: ContextVar[Transaction | None] = ContextVar(
            "_current_transaction", default=None
        )

    async def commit(self) -> None:
        session = self._get_session()

        if not session.is_active:
            await self.rollback()
            raise ValueError("Session is inactive")

        try:
            await session.commit()
        except Exception as e:
            raise RepositoryError("Unnable to commit transaction") from e

    async def rollback(self) -> None:
        session = self._get_session()

        try:
            await session.rollback()
        except Exception as e:
            raise RepositoryError("Unnable to rollback transaction") from e

    async def close(self) -> None:
        session = self._get_session()

        try:
            await session.close()
        except Exception as e:
            raise RepositoryError("Unnable to close session connection") from e

    async def __aenter__(self) -> Self:
        if not self._transaction_exists():
            tx = self._create_transaction()
            self._set_transaction(tx)
        else:
            tx = self._get_transaction()
            tx.enter()
        return self

    async def __aexit__(
        self,
        exc_type: type[Exception] | None,
        exc_val: Exception | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._finalize_transaction(exc_type is not None)
        if exc_val:
            self._handle_exception(exc_val)

    @asynccontextmanager
    async def get_session(
        self,
    ) -> AsyncGenerator[AsyncSession, None]:
        """Context manager for obtaining a session.

        - Uses the current session if it exists.
        - Otherwise, creates a temporary one, commits/rolls back, and closes it.
        """
        if self._transaction_exists():
            yield self._get_session()
            return

        async with self as uow:
            yield uow._get_session()  # noqa: SLF001

    async def _finalize_transaction(self, has_error: bool) -> None:
        if not self._transaction_exists():
            return

        tx = self._get_transaction()
        if has_error:
            await self.rollback()
        elif tx.should_commit():
            await self.commit()

        if tx.should_commit():  # Out of context manager
            await self.close()
            self._reset_session()
        else:
            tx.exit()

    def _handle_exception(self, exception: BaseException) -> None:
        if isinstance(exception, ApplicationError):
            raise exception

        if isinstance(exception, sqlalchemy.orm.exc.StaleDataError):
            raise OptimisticLockError() from exception

        if isinstance(exception, sqlalchemy.exc.DatabaseError):
            if isinstance(exception.orig, psycopg2.errors.UniqueViolation):
                field, value = self._extract_duplicate_info(exception.orig)
                raise DuplicateEntryError(field, value) from exception
            raise IntegrityError() from exception

        if isinstance(exception, sqlalchemy.exc.SQLAlchemyError):
            raise RepositoryError(f"{exception}", cause=exception) from exception

        raise exception

    def _extract_duplicate_info(self, error: BaseException) -> tuple[str, str]:
        match = re.search(r"\((\w+)\)=\((.*?)\)", str(error))
        if match:
            return match.group(1), match.group(2)
        return "unknown_field", "unknown_value"

    def _get_session(self) -> AsyncSession:
        return self._get_transaction().session

    def _get_transaction(self) -> Transaction:
        tx = self._current_transaction.get()
        if tx is None:
            raise ValueError("Transaction not found")
        return tx

    def _transaction_exists(self) -> bool:
        return self._current_transaction.get() is not None

    def _create_transaction(self) -> Transaction:
        session = self.session_factory.create()
        return Transaction(session, 0)

    def _set_transaction(self, session: Transaction) -> None:
        self._current_transaction.set(session)

    def _reset_session(self) -> None:
        self._current_transaction.set(None)
