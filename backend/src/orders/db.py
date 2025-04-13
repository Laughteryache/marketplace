from collections import Counter
from typing import List

from loguru import logger
from sqlalchemy import update, select, Integer, cast, func
from sqlalchemy.dialects.postgresql import array, ARRAY
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.db_core.tables import UsersCart
from backend.src.orders.models import ProductCartInfo
from backend.src.products.db import BusinessDB


class UsersDB:

    @staticmethod
    @logger.catch
    async def get_cart(
            session: AsyncSession,
            user_id: int
    ) -> List[ProductCartInfo]:
        result = await session.execute(
            select(UsersCart)
            .where(UsersCart.user_id == int(user_id)))
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
            .where(UsersCart.user_id == int(user_id))
        )
        await session.commit()

    @staticmethod
    @logger.catch
    async def drop_cart_item(
            user_id: int,
            product_id: int,
            session: AsyncSession,
    ) -> bool:
        result = await session.execute(
            select(UsersCart)
            .where(UsersCart.user_id == int(user_id)))
        user = result.scalar()

        if not user or not user.shopping_cart:
            return False
        try:
            updated_cart = user.shopping_cart.copy()
            updated_cart.remove(product_id)
        except ValueError:
            return False

        await session.execute(
            update(UsersCart)
            .where(UsersCart.user_id == int(user_id))
            .values(shopping_cart=updated_cart))
        await session.commit()
        return True

    @staticmethod
    @logger.catch
    async def add_cart_item(
            product_id: int,
            user_id: int,
            session: AsyncSession,
    ) -> None:
        await session.execute(
            update(UsersCart)
            .where(UsersCart.user_id == int(user_id))
            .values(
                shopping_cart=(
                        func.coalesce(
                            UsersCart.shopping_cart,
                            cast(array([], type_=ARRAY(Integer)), ARRAY(Integer))
                        ) + array([product_id]))))
        await session.commit()
