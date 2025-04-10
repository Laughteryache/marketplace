from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from loguru import logger
from typing import List

from backend.src.db_core.tables import BusinessProfile, BusinessFinance, UsersBalance
from backend.src.profile.models import BusinessProfileScheme

class BusinessDB:
    @staticmethod
    @logger.catch
    async def save_avatar_id(
            file_id: str,
            session: AsyncSession,
            business_id: id
    ) -> None:
        await session.execute(
            update(BusinessProfile)
            .where(BusinessProfile.business_id == int(business_id))
            .values(logo_id=file_id)
        )
        await session.commit()

    @staticmethod
    @logger.catch
    async def update_profile(
            creds: BusinessProfileScheme,
            business_id: id,
            session: AsyncSession
    ) -> None:
        await session.execute(
            update(BusinessProfile)
            .where(BusinessProfile.business_id == int(business_id))
            .values(
                title=creds.title,
                description=creds.description,
                location=creds.location))
        await session.commit()

    @staticmethod
    @logger.catch
    async def get_profile(
            id: id,
            session: AsyncSession
    ) -> BusinessProfile:
        result = await session.execute(
            select(BusinessProfile)
            .where(BusinessProfile.business_id == int(id)))
        return result.scalar()

    @staticmethod
    @logger.catch
    async def get_categories(session: AsyncSession) -> List[int]:
        result = await session.execute(select(Category.id))
        return result.scalars().all()

    @staticmethod
    @logger.catch
    async def get_balance(
            business_id: id,
            session: AsyncSession
    ) -> int:
        result = await session.execute(
            select(BusinessFinance.balance)
            .where(BusinessFinance.business_id==int(business_id)))
        return int(result.scalar())

class UsersDB:

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

