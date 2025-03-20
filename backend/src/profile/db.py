class BusinessDB:
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

    @logger.catch
    async def get_profile(
            id: id,
            session: AsyncSession
    ) -> BusinessProfile:
        result = await session.execute(
            select(BusinessProfile)
            .where(BusinessProfile.business_id == int(id)))
        return result.scalar()


    @logger.catch
    async def get_categories(session: AsyncSession) -> List[int]:
        result = await session.execute(select(Category.id))
        return result.scalars().all()


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

