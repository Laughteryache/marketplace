import time

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, update
from typing import List

import datetime

from .models import BusinessUploadProductScheme, ProductGetScheme, CategoryModel
from db_core.tables import Product, ProductDate, ProductData, ProductQuantity, Category


class BusinessDB:

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
                quanity=creds.quanity), ]

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
                adult_only=creds.adult_only)
        )

        session.add_all(registration_data)
        await session.commit()
        return product_id

    @staticmethod
    @logger.catch
    async def get_categories_ids(session: AsyncSession) -> Category:
        result = await session.execute(select(Category.id).order_by(Category.id))
        return result.scalars().all()

    @staticmethod
    @logger.catch
    async def get_categories(
            session: AsyncSession,
            id: int | None = None,
    ) -> CategoryModel | List[CategoryModel]:
        if id:
            result = await session.execute(select(Category).where(Category.id == id))
            category = result.scalar()
            if not category:
                return None
            if category.is_deleted is True:
                return None
            return CategoryModel(
                category_id=category.id,
                name=category.name,
                description=category.description)
        else:
            result = await session.execute(select(Category).order_by(Category.id))
            categories = result.scalars().all()
            categories_list = []
            for category in categories:
                if category.is_deleted is True:
                    continue
                categories_list.append(
                    CategoryModel(
                        category_id=category.id,
                        name=category.name,
                        description=category.description))
            return categories_list

    @staticmethod
    @logger.catch
    async def get_product(
            id: int,
            session: AsyncSession
    ) -> ProductGetScheme:
        product_result = await session.execute(select(Product).where(Product.id == id))
        product_data_result = await session.execute(select(ProductData).where(ProductData.product_id == id))
        product_date_result = await session.execute(select(ProductDate).where(ProductDate.product_id == id))
        product_quanity = await session.execute(select(ProductQuantity).where(ProductQuantity.product_id == id))

        product = product_result.scalar()
        product_data = product_data_result.scalar()
        product_quanity = product_quanity.scalar()
        if product_quanity:
            if product_quanity == 0:
                return None
        product_date = product_date_result.scalar()
        if not product:
            return None
        if product.is_deleted is True:
            return None
        start_date = product_date.start_date.date()

        if product_date.end_date:
            if datetime.datetime.fromtimestamp(time.time()) >= product_date.end_date:
                return None
            if product_date.start_date > product_date.end_date:
                return None
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

    @staticmethod
    @logger.catch
    async def search_product(
            session: AsyncSession,
            name: str,
            start_id: int
    ) -> ProductGetScheme | List[ProductGetScheme]:
        name = name.lstrip().rstrip()
        limit = 30
        semi_product_data = None
        result = await session.execute(
            select(Product)
            .order_by(Product.id.asc())
            .limit(limit)
            .where(Product.name.ilike(f"%{name}%"), Product.id >= start_id))
        product_data = result.scalars().all()
        if not product_data:
            result = await session.execute(
                select(Product)
                .order_by(Product.id.asc())
                .limit(limit)
                .where(Product.name.ilike(f"%{name.replace(' ', '%')}%"), Product.id >= start_id))
            product_data = result.scalars().all()

        elif len(product_data) < limit:
            limit = limit - len(product_data)
            result = await session.execute(
                select(Product)
                .order_by(Product.id.asc())
                .limit(limit)
                .where(Product.name.ilike(f"%{name.replace(' ', '%')}%"), Product.id > product_data[-1].id))
            semi_product_data = result.scalars().all()
        if not product_data and not semi_product_data:
            return None
        product_get_list = []
        if product_data:
            for product in product_data:
                cur_product_data = await BusinessDB.get_product(id=product.id, session=session)
                if cur_product_data:
                    product_get_list.append(cur_product_data)
        if semi_product_data:
            for product in semi_product_data:
                cur_product_data = await BusinessDB.get_product(id=product.id, session=session)
                if cur_product_data:
                    product_get_list.append(cur_product_data)
        return product_get_list


    async def save_product_image_id(
            session: AsyncSession,
            file_id: str,
            product_id: int,
    ) -> None:
        await session.execute(
            update(ProductData)
            .where(ProductData.product_id == product_id)
            .values(logo_path=file_id))
        await session.commit()