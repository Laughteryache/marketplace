from datetime import datetime
from collections import Counter
from typing import List

from loguru import logger
from sqlalchemy import update, select, Integer, cast, func, text
from sqlalchemy.dialects.postgresql import array, ARRAY, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import session_user, coalesce

from backend.src.db_core.tables import (UsersCart, Order, OrderCart, ProductQuanity, Product,
                                        OrderDate, OrderPrice, UsersBalance, BusinessFinance)
from backend.src.orders.models import ProductCartInfo
from backend.src.products.db import BusinessDB as ProductBusinessDB
from backend.src.profile.db import UsersDB as ProfileUsersDB


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
            product_data = await ProductBusinessDB.get_product(id=product_id, session=session)
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
            .where(UsersCart.user_id == int(user_id)))
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

    @staticmethod
    @logger.catch
    async def check_cart(
            user_id: int,
            session: AsyncSession,
    ) -> bool | None:
        user_cart_result = await session.execute(
            select(UsersCart)
            .where(UsersCart.user_id == int(user_id)))
        user_cart = user_cart_result.scalar()
        if not user_cart:
            return None
        if not user_cart.shopping_cart:
            return False
        return True

    @staticmethod
    @logger.catch
    async def check_balance(
            session: AsyncSession,
            user_id: int,
            cart: list[ProductCartInfo],
    ) -> bool:
        cart_price = 0
        if not cart:
            return False
        for product in cart:
            cart_price += product.product_data.price*product.quantity

        balance = await ProfileUsersDB.get_balance(session=session, user_id=user_id)
        if cart_price > balance:
            return False
        return int(cart_price)

    @staticmethod
    @logger.catch
    async def register_order(
            session: AsyncSession,
            user_id: int,
            cart_price: int,
    ) -> int:
        order_insert_result = await session.execute(
            insert(Order)
            .values(
                creator_id=user_id,
                is_canceled=False,
                is_deleted=False)
            .returning(Order.id))
        order_id = order_insert_result.scalar()
        cart_result = await session.execute(
            select(UsersCart.shopping_cart)
            .where(UsersCart.user_id == int(user_id)))
        cart = cart_result.scalar()
        order_data = [
            OrderDate(
                order_id=order_id,
                start_date=datetime.utcnow()),
            OrderCart(
                order_id=order_id,
                shopping_cart=cart),
            OrderPrice(
                order_id=order_id,
                price=cart_price)
        ]
        session.add_all(order_data)
        await session.execute(
            update(UsersCart)
            .where(UsersCart.user_id == int(user_id))
            .values(shopping_cart=[]))
        await session.execute(
            update(UsersBalance)
            .where(UsersBalance.user_id == int(user_id))
            .values(balance=coalesce(UsersBalance.balance, 0) - int(cart_price))
        )
        for id in cart:
            await session.execute(
                update(ProductQuanity)
                .where(ProductQuanity.product_id == id)
                .values(quanity=coalesce(ProductQuanity.quanity, 0) - 1))
            result = await session.execute(
                select(Product)
                .where(Product.id==id))
            product = result.scalar()
            await session.execute(
                update(BusinessFinance)
                .values(
                    revenue=coalesce(BusinessFinance.revenue, 0) + product.price,
                    balance=coalesce(BusinessFinance.balance, 0)+(product.price*0.98),
                    earnings=coalesce(BusinessFinance.earnings, 0)+(product.price*0.98))
                .where(BusinessFinance.business_id==product.creator_id))
        await session.commit()
        return order_id

    @staticmethod
    @logger.catch
    async def get_active_orders(
            session: AsyncSession,
            user_id: int,
    ):
        query = text("""
        SELECT
            oc.order_id,
            oc.shopping_cart
        FROM order_cart oc
            JOIN orders o ON o.id = oc.order_id
                WHERE o.creator_id = :user_id
                    AND o.is_canceled = false
                    AND o.is_deleted = false;
        """)
        order_result = await session.execute(query, { 'user_id': user_id })
        return order_result.mappings().all()

    @staticmethod
    @logger.catch
    async def check_quanity(
            session: AsyncSession,
            cart: list[ProductCartInfo]
    ) -> bool:
        for product in cart:
            result = await session.execute(
                select(ProductQuanity)
                .where(ProductQuanity.product_id == product.product_data.product_id))
            db_product = result.scalar()
            if db_product.quanity < product.quantity:
                return [product.product_data.product_id, product.quantity - db_product.quanity]
        return True

class BusinessDB:

    @staticmethod
    @logger.catch
    async def get_active_orders(
            session: AsyncSession,
            business_id: int
    ):
        query = text("""
            SELECT
                order_id,
                filtered_cart AS shopping_cart
            FROM (
                SELECT
                    order_id,
                    ARRAY(
                        SELECT p.id
                        FROM unnest(shopping_cart) AS product_id
                        JOIN products p ON p.id = product_id
                        WHERE creator_id = :business_id AND is_deleted = false
                    ) AS filtered_cart
                FROM order_cart
            ) sub
            WHERE array_length(filtered_cart, 1) > 0; 
        """) # Зубодробительный SQL-запрос
        result = await session.execute(query, {"business_id": business_id})
        return result.mappings().all()




