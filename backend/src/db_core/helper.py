from typing import AsyncGenerator
from loguru import logger
from sqlalchemy.ext.asyncio import (create_async_engine, AsyncEngine,
                                    async_sessionmaker, AsyncSession)

from backend.src.global_config import settings
from backend.src.db_core.tables import *



class DatabaseHelper:
    def __init__(
            self,
            url: str,
            echo: bool = True,
            echo_pool: bool = False,
            pool_size: int = 5,
            max_overflow: int = 10, ) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow, )

        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False, )

    @logger.catch
    async def dispose(self) -> None:
        await self.engine.dispose()

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session



db_helper = DatabaseHelper(
    url=settings.db.DATABASE_URL,
    echo=False,
    echo_pool=False,
    pool_size=settings.db.POOL_SIZE,
    max_overflow=settings.db.MAX_OVERFLOW,
)
