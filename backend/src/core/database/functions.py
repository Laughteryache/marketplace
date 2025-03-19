from sqlalchemy import update, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


from typing import List
import datetime


from loguru import logger

from ..config import settings
from .helper import db_helper
from .tables import *
from ..schemes import (SignUpScheme, SignInScheme, BusinessProfileScheme,
                       BusinessUploadProductScheme, ProductGetScheme)

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

        query = text("""
            INSERT INTO businesses (login, email, hashed_password, is_deleted)
            VALUES (:login, :email, :hashed_password, FALSE)
            RETURNING id;""")

        result = await session.execute(query, {
            "login": creds.login,
            "email": creds.email,
            "hashed_password": hashed_password})

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
            business_id: id,
            session: AsyncSession
    ) -> Business:
        result = await session.execute(
            select(Business)
            .where(Business.id==int(business_id)))
        return result.scalar()

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

    @staticmethod
    @logger.catch
    async def save_avatar_id(
            file_id: str,
            session: AsyncSession,
            business_id: id
    ) -> None:
         await session.execute(
             update(BusinessProfile)
             .where(BusinessProfile.business_id==int(business_id))
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
            .where(BusinessProfile.business_id==int(business_id))
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
            .where(BusinessProfile.business_id==int(id)))
        return result.scalar()

    @staticmethod
    @logger.catch
    async def get_categories(session: AsyncSession) -> List[int]:
        result = await session.execute(select(Category.id))
        return result.scalars().all()

    @staticmethod
    @logger.catch
    async def create_product(
            creds: BusinessUploadProductScheme,
            business_id: id,
            session: AsyncSession
    ) -> str:

        query = text("""
            INSERT INTO products (price, name, category_id, creator_id, is_deleted)
            VALUES (:price, :name, :category_id, :creator_id, FALSE)
            RETURNING id;""")

        result = await session.execute(query, {
            "price": creds.price,
            "name": creds.name,
            "category_id": creds.category_id,
            "creator_id": business_id})
        await session.commit()
        product_id = result.scalar()
        registration_data = [
            ProductQuantity(
                product_id=product_id,
                quanity=creds.quanity),]

        start_date_datetime_obj = datetime.datetime.combine(creds.start_date, datetime.time.min,
                                                            tzinfo=datetime.timezone.utc)
        start_date_timestamp = round(start_date_datetime_obj.timestamp())
        start_date_timestamp = datetime.datetime.fromtimestamp(start_date_timestamp, tz=None)
        if creds.end_date:
            end_date_datetime_obj = datetime.datetime.combine(creds.end_date, datetime.time.max,
                                                              tzinfo=datetime.timezone.utc)
            end_date_timestamp = round(end_date_datetime_obj.timestamp())
            end_date_timestamp = datetime.datetime.fromtimestamp(end_date_timestamp, tz=None)

            registration_data.append(
                ProductDate(
                    product_id=product_id,
                    start_date=start_date_timestamp,
                    end_date=end_date_timestamp)
            )
        else:
            registration_data.append(
                ProductDate(
                    product_id=product_id,
                    start_date=start_date_timestamp))

        registration_data.append(
            ProductData(
                product_id=product_id,
                description=creds.description,
                sex=creds.sex,
                adult_only=creds.adult_only))
        session.add_all(registration_data)
        await session.commit()
        return product_id


    @staticmethod
    @logger.catch
    async def get_product(
            id: int,
            session: AsyncSession
    ) -> ProductGetScheme:
        product_result = await session.execute(select(Product).where(Product.id==id))
        product_data_result = await session.execute(select(ProductData).where(ProductData.product_id==id))
        product_date_result = await session.execute(select(ProductDate).where(ProductDate.product_id==id))
        product_quanity = await session.execute(select(ProductQuantity).where(ProductQuantity.product_id==id))

        product = product_result.scalar()
        product_data = product_data_result.scalar()
        product_quanity = product_quanity.scalar()
        product_date = product_date_result.scalar()
        if not product:
            return None
        if product.is_deleted is True:
            return None
        start_date = product_date.start_date.date()
        if product_date.end_date:
            end_date = product_date.end_date.date()
        else:
            end_date = None

        if product_data.logo_path:
            return ProductGetScheme(
                product_id=product.id,
                name=product.name,
                description=product_data.description,
                category_id=product.category_id,
                price=product.price,
                logo_path=f"https://drive.google.com/file/d/{product_data.logo_path}/preview",
                sex=product_data.sex,
                adult_only=product_data.adult_only,
                start_date=str(start_date),
                end_date=str(end_date),
                quanity=product_quanity.quanity,
                creator_id=product.creator_id)
        return ProductGetScheme(
            product_id=product.id,
            name=product.name,
            description=product_data.description,
            category_id=product.category_id,
            price=product.price,
            sex=product_data.sex,
            adult_only=product_data.adult_only,
            start_date=str(start_date),
            end_date=str(end_date),
            quanity=product_quanity.quanity,
            creator_id=product.creator_id)

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
                last_login=datetime.datetime.utcnow(),
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
