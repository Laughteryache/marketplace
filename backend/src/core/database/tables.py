from sqlalchemy import Column, Integer, String, BigInteger, Boolean, SmallInteger, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase, declared_attr
from sqlalchemy import MetaData
from src.utils.camel_case_converter import camel_case_to_snake_case


class Base(DeclarativeBase):
    __abstract__ = True

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_N_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return camel_case_to_snake_case(cls.__name__)


class User(Base):
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    login = Column(String(25), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(50), nullable=False)
    role = Column(String(10), nullable=False)
    is_deleted = Column(Boolean, nullable=False)

    reviews = relationship("Review", backref="creator")
    orders = relationship("Order", backref="creator")


class Business(Base):
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    login = Column(String(25), unique=True, nullable=False)
    hashed_password = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    is_deleted = Column(Boolean, nullable=False)

    products = relationship("Product", backref="creator")
    promocodes = relationship("Promocode", backref="creator")
    orders = relationship("Order", backref="business")
    finances = relationship("BusinessFinance", uselist=False, backref="business")
    profile = relationship("BusinessProfile", uselist=False, backref="business")


class Review(Base):
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    creator_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    product_id = Column(BigInteger, ForeignKey('products.id'), nullable=False)
    rate = Column(SmallInteger, nullable=False)
    is_deleted = Column(Boolean, nullable=False)

    data = relationship("ReviewData", uselist=False, backref="review")


class Product(Base):
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    price = Column(BigInteger, nullable=False)
    name = Column(String(50), nullable=False)
    creator_id = Column(BigInteger, ForeignKey('businesses.id'), nullable=False)
    category_id = Column(SmallInteger, ForeignKey('categories.id'), nullable=False)
    is_deleted = Column(Boolean, nullable=False)

    reviews = relationship("Review", backref="product")
    orders = relationship("Order", secondary="order_cart", backref="products")
    data = relationship("ProductData", uselist=False, backref="product")
    quantity = relationship("ProductQuantity", uselist=False, backref="product")
    date = relationship("ProductDate", uselist=False, backref="product")


class Category(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(500), nullable=False)
    is_deleted = Column(Boolean, nullable=False)

    products = relationship("Product", backref="category")


class Order(Base):
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    creator_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    business_id = Column(BigInteger, ForeignKey('businesses.id'), nullable=False)
    promocode_id = Column(BigInteger, ForeignKey('promocodes.id'))
    is_canceled = Column(Boolean, nullable=False)
    is_deleted = Column(Boolean, nullable=False)

    date = relationship("OrderDate", uselist=False, backref="order")
    price = relationship("OrderPrice", uselist=False, backref="order")
    cart = relationship("OrderCart", uselist=False, backref="order")


class Promocode(Base):
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    creator_id = Column(BigInteger, ForeignKey('businesses.id'), nullable=False)
    product_id = Column(BigInteger, ForeignKey('products.id'), nullable=False)
    name = Column(String(255), nullable=False)

    discount = relationship("PromocodeDiscount", uselist=False, backref="promocode")
    quantity = relationship("PromoQuantity", uselist=False, backref="promocode")
    date = relationship("PromocodeDate", uselist=False, backref="promocode")


class UsersProfile(Base):
    user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
    last_login = Column(TIMESTAMP, nullable=False)
    date_joined = Column(TIMESTAMP, nullable=False)
    location = Column(String(90), nullable=False)


class UsersCart(Base):
    user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
    shopping_cart = Column(Integer, nullable=False)


class UsersBalance(Base):
    user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
    balance = Column(BigInteger, nullable=False)


class BusinessFinance(Base):
    business_id = Column(BigInteger, ForeignKey('businesses.id'), primary_key=True)
    balance = Column(BigInteger)
    revenue = Column(BigInteger)
    earnings = Column(BigInteger)


class BusinessProfile(Base):
    business_id = Column(BigInteger, ForeignKey('businesses.id'), primary_key=True)
    title = Column(String(50), nullable=False)
    description = Column(String(500), nullable=False)
    logo_path = Column(String(255))
    location = Column(String(90), nullable=False)
    date_joined = Column(TIMESTAMP, nullable=False)


class ProductData(Base):
    product_id = Column(BigInteger, ForeignKey('products.id'), primary_key=True)
    description = Column(String(500), nullable=False)
    logo_path = Column(String(255), nullable=False)
    sex = Column(String(15), nullable=False)
    adult_only = Column(Boolean, nullable=False)


class ProductQuantity(Base):
    product_id = Column(BigInteger, ForeignKey('products.id'), primary_key=True)
    quantity = Column(BigInteger)


class PromocodeDiscount(Base):
    promocode_id = Column(BigInteger, ForeignKey('promocodes.id'), primary_key=True)
    percent_off = Column(SmallInteger, nullable=False)
    discount = Column(SmallInteger, nullable=False)


class PromoQuantity(Base):
    promocode_id = Column(BigInteger, ForeignKey('promocodes.id'), primary_key=True)
    quantity = Column(BigInteger, nullable=False)


class PromocodeDate(Base):
    promocode_id = Column(BigInteger, ForeignKey('promocodes.id'), primary_key=True)
    start_date = Column(TIMESTAMP, nullable=False)
    end_date = Column(TIMESTAMP)


class ProductDate(Base):
    product_id = Column(BigInteger, ForeignKey('products.id'), primary_key=True)
    start_date = Column(TIMESTAMP, nullable=False)
    end_date = Column(TIMESTAMP)


class ReviewData(Base):
    id = Column(BigInteger, ForeignKey('reviews.id'), primary_key=True)
    title = Column(String(50), nullable=False)
    description = Column(String(500), nullable=False)


class OrderDate(Base):
    order_id = Column(BigInteger, ForeignKey('orders.id'), primary_key=True)
    start_date = Column(TIMESTAMP, nullable=False)
    end_date = Column(TIMESTAMP)


class OrderPrice(Base):
    order_id = Column(BigInteger, ForeignKey('orders.id'), primary_key=True)
    price = Column(BigInteger, nullable=False)
    discounted_price = Column(BigInteger, nullable=False)


class OrderCart(Base):
    order_id = Column(BigInteger, ForeignKey('orders.id'), primary_key=True)
    shopping_cart = Column(Integer, nullable=False)