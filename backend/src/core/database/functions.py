from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from .helper import db_helper
from .tables import *
from sqlalchemy.future import select

from typing import List

from loguru import logger


class Authorization:
    pass

class Business(Authorization):

    @staticmethod
    @logger.catch
    async def check_exists(
            session: AsyncSession,
            login: str | None = None,
            email: str | None = None,
    ) -> bool:
        pass

class User(Authorization):

    @staticmethod
    @logger.catch
    async def check_exists(
            session: AsyncSession,
            login: str | None = None,
            email: str | None = None
    ) -> bool:
        result = await session.execute(
            select(User.id)
            .where(User.login == login or User.email == email)
        )
        if result.scalar():
            return False
        return True