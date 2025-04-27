from sqlalchemy import (Column, Integer, String, BigInteger,
                        Boolean, SmallInteger, TIMESTAMP,
                        ARRAY, FLOAT)

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    __abstract__ = True


class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(500), nullable=False)
    role = Column(String(10), nullable=False)
    is_deleted = Column(Boolean, nullable=False)


class Business(Base):
    __tablename__ = 'businesses'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    hashed_password = Column(String(500), nullable=False)
    email = Column(String(50), nullable=False)
    is_deleted = Column(Boolean, nullable=False)


class Product(Base):
    __tablename__ = 'products'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    price = Column(BigInteger, nullable=False)
    name = Column(String(50), nullable=False)
    creator_id = Column(BigInteger)
    category_id = Column(SmallInteger)
    is_deleted = Column(Boolean, nullable=False)


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(500), nullable=False)
    is_deleted = Column(Boolean, nullable=False)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    creator_id = Column(BigInteger)
    business_id = Column(BigInteger)
    promocode_id = Column(BigInteger)
    is_canceled = Column(Boolean, nullable=False)
    is_deleted = Column(Boolean, nullable=False)


class UsersProfile(Base):
    __tablename__ = 'users_profile'
    user_id = Column(BigInteger, primary_key=True)
    last_login = Column(TIMESTAMP, nullable=False)
    date_joined = Column(TIMESTAMP, nullable=False)
    location = Column(String(90), nullable=False)


class UsersCart(Base):
    __tablename__ = 'users_cart'
    user_id = Column(BigInteger, primary_key=True)
    shopping_cart = Column(ARRAY(Integer), nullable=False)


class UsersBalance(Base):
    __tablename__ = 'users_balance'
    user_id = Column(BigInteger, primary_key=True)
    balance = Column(BigInteger, nullable=False)


class BusinessFinance(Base):
    __tablename__ = 'business_finances'
    business_id = Column(BigInteger, primary_key=True)
    balance = Column(FLOAT)
    revenue = Column(FLOAT)
    earnings = Column(FLOAT)


class BusinessProfile(Base):
    __tablename__ = 'business_profile'
    business_id = Column(BigInteger, primary_key=True)
    title = Column(String(50), nullable=False)
    description = Column(String(500), nullable=False)
    logo_id = Column(String(255))
    location = Column(String(90), nullable=False)
    date_joined = Column(TIMESTAMP, nullable=False)


class ProductData(Base):
    __tablename__ = 'product_data'
    product_id = Column(BigInteger, primary_key=True)
    description = Column(String(500), nullable=False)
    logo_path = Column(String(255), nullable=False)
    sex = Column(String(15), nullable=False)
    adult_only = Column(Boolean, nullable=False)


class ProductQuanity(Base):
    __tablename__ = 'product_quanity'
    product_id = Column(BigInteger, primary_key=True)
    quanity = Column(BigInteger)

class ProductDate(Base):
    __tablename__ = 'product_date'
    product_id = Column(BigInteger, primary_key=True)
    start_date = Column(TIMESTAMP, nullable=False)
    end_date = Column(TIMESTAMP)


class OrderDate(Base):
    __tablename__ = 'order_date'
    order_id = Column(BigInteger, primary_key=True)
    start_date = Column(TIMESTAMP, nullable=False)
    end_date = Column(TIMESTAMP)


class OrderPrice(Base):
    __tablename__ = 'order_price'
    order_id = Column(BigInteger, primary_key=True)
    price = Column(BigInteger, nullable=False)


class OrderCart(Base):
    __tablename__ = 'order_cart'
    order_id = Column(BigInteger, primary_key=True)
    shopping_cart = Column(ARRAY(Integer), nullable=False)
