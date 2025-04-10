from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, insert
from datetime import datetime
from loguru import logger

from backend.src.auth.models import SignUpScheme, SignInScheme
from backend.src.auth.utils import HashSecurity
from backend.src.db_core.tables import (User, UsersBalance, UsersCart, UsersProfile,
                                Business, BusinessFinance, BusinessProfile)

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

        result = await session.execute(
            insert(Business)
            .values(email=creds.email,
                    hashed_password=hashed_password,
                    is_deleted=False)
            .returning(Business.id))
        await session.commit()
        business_id = result.scalar()

        registration_data = [
            BusinessFinance(
                business_id=business_id,
                balance=0,
                revenue=0,
                earnings=0),
            BusinessProfile(
                business_id=business_id,
                title='',
                description='',
                location='Чайковский',
                date_joined=datetime.utcnow())
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
            business_id: id,
            session: AsyncSession
    ) -> Business:
        result = await session.execute(
            select(Business)
            .where(Business.id==int(business_id)))
        return result.scalar()


class UsersDB:

    @staticmethod
    @logger.catch
    async def check_exists(
            session: AsyncSession,
            creds: SignUpScheme
    ) -> bool:
        result = await session.execute(
            select(User)
            .where(User.email==creds.email))
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
        result = await session.execute(
            insert(User)
            .values(email=creds.email, hashed_password=hashed_password,
                    role=creds.role, is_deleted=False)
            .returning(User.id))

        await session.commit()
        user_id = result.scalar()

        registration_data = [
            UsersBalance(
                user_id=user_id,
                balance=0),
            UsersCart(user_id=user_id),
            UsersProfile(
                user_id=user_id,
                last_login=datetime.utcnow(),
                date_joined=datetime.utcnow(),
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
            user_id: id,
            session: AsyncSession
    ) -> User:
        result = await session.execute(
            select(User)
            .where(User.id == int(user_id)))
        return result.scalar()