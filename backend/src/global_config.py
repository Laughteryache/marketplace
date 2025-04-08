from pydantic_settings import BaseSettings
from time import time
from loguru import logger
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseSettings(BaseSettings):
    DATABASE_URL: str
    POOL_SIZE: int = 50
    MAX_OVERFLOW: int = 10

class RoutersPrefix(BaseSettings):
    AUTH: str
    PRODUCTS: str
    PROFILE: str
    ORDER: str


class LoggerSettings(BaseSettings):
    filename: str = "app"
    extension: str = ".log"
    level: str = "DEBUG"
    rotation: str = "12:00"
    serialize: bool = False
    compression: str = "zip"
    format: str = "{time} {level} {message}"


class Settings(BaseSettings):
    SERVER_START_TIME: int
    SERVER_PORT: int = 8765
    IP_ADDRESS: str = 'localhost'
    db: DatabaseSettings
    prefix: RoutersPrefix
    logger: LoggerSettings



settings = Settings(
    SERVER_START_TIME=int(time()),
    SERVER_PORT=int(os.getenv("SERVER_PORT")),
    IP_ADDRESS=os.getenv("IP_ADDRESS"),
    db=DatabaseSettings(
        DATABASE_URL=os.getenv('DB_URL'),
        POOL_SIZE=int(os.getenv('POOL_SIZE')),
        MAX_OVERFLOW=int(os.getenv('MAX_OVERFLOW')),
    ),
    prefix=RoutersPrefix(
        AUTH='/v1/api/auth',
        PRODUCTS='/v1/api/products',
        PROFILE='/v1/api/profile',
        ORDER='/v1/api/order',

    ),
    logger=LoggerSettings(
        filename="app",
        extension=".log",
        level="DEBUG",
        compression="zip",
        rotation="5MB",
        serialize=False,
        format="{time} {level} {message}"
    ),
)


logger.add(
    sink=f'{settings.logger.filename}{settings.logger.extension}',
    level=settings.logger.level,
    format=settings.logger.format,
    serialize=settings.logger.serialize,
    rotation=settings.logger.rotation,
    compression=settings.logger.compression,
)

