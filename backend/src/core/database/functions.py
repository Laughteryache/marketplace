from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from typing import List

from loguru import logger

from .helper import db_helper
from .tables import *
from ..schemes import UserSignUpScheme, UserSignInScheme
from services.security import HashSecurity


class BusinessDB:

    @staticmethod
    @logger.catch
    async def check_exists(
            session: AsyncSession,
            login: str | None = None,
            email: str | None = None
    ) -> bool:
        pass

class UsersDB:
    @staticmethod
    @logger.catch
    async def check_exists(
            session: AsyncSession,
            email: str
    ) -> bool:
        result = await session.execute(
            select(User)
            .where(User.email == email))
        if result.scalar():
            return False
        return True

    @staticmethod
    @logger.catch
    async def register(
            session: AsyncSession,
            creds: UserSignUpScheme
    ) -> str | None:
        hashed_password = await HashSecurity.get_hash(creds.password)
        registration_data = [
            User(
            login=creds.login,
            email=creds.email,
            hashed_password=hashed_password,
            role='user',
            is_deleted=False)
        ]
        session.add_all(registration_data)
        await session.commit()
        await session.refresh(registration_data[0])
        result = await session.execute(
            select(User.id)
            .where(User.login==creds.login and
                    User.email==creds.email))
        return result.scalar()

    @staticmethod
    @logger.catch
    async def verify_password(
            session: AsyncSession,
            creds: UserSignInScheme
    ) -> bool:
        result = await session.execute(
            select(User.hashed_password)
            .where(User.email==creds.email))
        db_hashed_password = result.scalar()
        return await HashSecurity.verify_hash(message=creds.password, hashed_message=db_hashed_password)

    @staticmethod
    @logger.catch
    async def get_id(
            session: AsyncSession,
            creds: UserSignInScheme
    ) -> str:
        result = await session.execute(
            select(User.id)
            .where(User.email==creds.email)
        )
        return result.scalar()