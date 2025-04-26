from contextlib import asynccontextmanager
from typing import Annotated, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import func, inspect
from sqlalchemy.orm import Mapped, sessionmaker, DeclarativeBase, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, AsyncAttrs, create_async_engine


created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[
    datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)
]

str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    def __repr__(self):
        return f'{self.__class__.__name__}({self.id!r})'


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(db_url)
        self._session_factory = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_models(self):
        async with self._engine.begin() as session:
            await session.run_sync(Base.metadata.drop_all)
            await session.run_sync(Base.metadata.create_all)

    async def check_and_create_tables(self):
        async with self._engine.connect() as conn:
            tables = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_table_names()
            )
        expected_tables = Base.metadata.tables

        if not all(table in tables for table in expected_tables):
            await self.init_models()
            print('Таблицы созданы!')

    async def drop_models(self):
        async with self._engine.begin() as session:
            await session.run_sync(Base.metadata.drop_all)

    @asynccontextmanager
    async def session(self):
        async with self._session_factory() as session:
            try:
                yield session
            finally:
                await session.close()
