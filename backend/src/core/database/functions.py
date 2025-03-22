from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from typing import List
import datetime


from loguru import logger

from ..config import settings
from .helper import db_helper
from .tables import *
from ..schemes import SignUpScheme, SignInScheme
from services.security import HashSecurity


class BusinessDB:

    @staticmethod
    @logger.catch
    async def check_exists(
            session: AsyncSession,
            creds: SignUpScheme
    ) -> bool:
        result = await session.execute(
            select(Business)
            .where(Business.email == creds.email))
        if result.scalar():
            return False
        return True

    @staticmethod
    @logger.catch
    async def register(
            session: AsyncSession,
            creds: SignUpScheme
    ) -> str:
        hashed_password = await HashSecurity.get_hash(creds.password)
        registration_data = [
            Business(
                login=creds.login,
                email=creds.email,
                hashed_password=hashed_password,
                is_deleted=False),
        ]
        session.add_all(registration_data)
        await session.commit()
        await session.refresh(registration_data[0])
        result = await session.execute(
            select(Business.id)
            .where(Business.email==creds.email))
        business_id = result.scalar()
        registration_data = [
            BusinessFinance(
                business_id=business_id,
                balance=0,
                revenue=0,
                earnings=0),
            BusinessProfile(
                business_id=business_id,
                location='Чайковский',
                date_joined=datetime.datetime.utcnow())
        ]
        session.add_all(registration_data)
        await session.commit()
        return business_id

    @staticmethod
    @logger.catch
    async def get_id(
            session: AsyncSession,
            creds: SignInScheme
    ) -> str:
        result = await session.execute(
            select(Business.id)
            .where(Business.email==creds.email))
        return result.scalar()

    @staticmethod
    @logger.catch
    async def verify_password(
            session: AsyncSession,
            creds: SignInScheme
    ) -> bool:
        result = await session.execute(
            select(Business.hashed_password)
            .where(Business.email==creds.email))
        db_hashed_password = result.scalar()
        return await HashSecurity.verify_hash(message=creds.password, hashed_message=db_hashed_password)

    @staticmethod
    @logger.catch
    async def get_data_by_id(
            user_id: str,
            session: AsyncSession
    ) -> Business:
        result = await session.execute(
            select(Business)
            .where(Business.id==int(user_id)))
        return result.scalar()

    @staticmethod
    @logger.catch
    async def get_balance(
            business_id: str,
            session: AsyncSession
    ) -> int:
        result = await session.execute(
            select(BusinessFinance.balance)
            .where(BusinessFinance.business_id==int(business_id)))
        return int(result.scalar())



class UsersDB:

    @staticmethod
    @logger.catch
    async def check_exists(
            session: AsyncSession,
            creds: SignUpScheme
    ) -> bool:
        email_result = await session.execute(
            select(User)
            .where(User.email==creds.email))
        login_result = await session.execute(
            select(User)
            .where(User.login==creds.login))
        if email_result.scalar() or login_result.scalar():
            return False
        return True

    @staticmethod
    @logger.catch
    async def register(
            session: AsyncSession,
            creds: SignUpScheme
    ) -> str | None:
        hashed_password = await HashSecurity.get_hash(creds.password)
        registration_data = [
            User(
            login=creds.login,
            email=creds.email,
            hashed_password=hashed_password,
            role='user',
            is_deleted=False),
        ]
        session.add_all(registration_data)
        await session.commit()
        await session.refresh(registration_data[0])
        result = await session.execute(
            select(User.id)
            .where(User.email==creds.email))
        user_id = result.scalar()

        registration_data = [
            UsersBalance(
                user_id=user_id,
                balance=0),
            UsersCart(
                user_id=user_id,
                shopping_cart=[]),
            UsersProfile(
                user_id=user_id,
                last_login=datetime.datetime.now(),
                date_joined=datetime.datetime.utcnow(),
                location='Чайковский')
        ]
        session.add_all(registration_data)
        await session.commit()
        return user_id


    @staticmethod
    @logger.catch
    async def verify_password(
            session: AsyncSession,
            creds: SignInScheme
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
            creds: SignInScheme
    ) -> str:
        result = await session.execute(
            select(User.id)
            .where(User.email==creds.email)
        )
        return result.scalar()

    @staticmethod
    @logger.catch
    async def get_data_by_id(
            user_id: str,
            session: AsyncSession
    ) -> User:
        result = await session.execute(
            select(User)
            .where(User.id==int(user_id)))
        return result.scalar()

    @staticmethod
    @logger.catch
    async def get_balance(
            user_id: str,
            session: AsyncSession
    ) -> int:
        result = await session.execute(
            select(UsersBalance.balance)
            .where(UsersBalance.user_id==int(user_id)))
        return int(result.scalar())
