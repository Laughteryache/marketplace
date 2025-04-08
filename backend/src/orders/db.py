from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, delete
from db_core.tables import UsersCart

from loguru import logger
from collections import Counter
from typing import List

from products.db import BusinessDB
from .models import ProductCartInfo


class UsersDB:

    @staticmethod
    @logger.catch
    async def get_cart(
            session: AsyncSession,
            user_id: int
    ) -> List[ProductCartInfo]:
        result = await session.execute(
            select(UsersCart)
            .where(UsersCart.user_id==int(user_id)))
        products_ids = result.scalar()
        if not products_ids.shopping_cart:
            return None
        cart = Counter(products_ids.shopping_cart)
        serialized_cart = []
        for product_id, count in cart.items():
            product_data = await BusinessDB.get_product(id=product_id, session=session)
            if product_data:
                serialized_cart.append(
                    ProductCartInfo(
                        product_data=product_data,
                        quantity=count))
        return serialized_cart

    @staticmethod
    @logger.catch
    async def drop_cart_items(
            session: AsyncSession,
            user_id: int
    ) -> None:
        await session.execute(
            update(UsersCart)
            .values(shopping_cart=[])
            .where(UsersCart.user_id==int(user_id))
        )
        await session.commit()