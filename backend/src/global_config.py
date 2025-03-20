from pydantic_settings import BaseSettings
from time import time
from loguru import logger
from datetime import timedelta


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str
    POOL_SIZE: int = 50
    MAX_OVERFLOW: int = 10

class RoutersPrefix(BaseSettings):
    AUTH: str


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
    SERVER_PORT=8765,
    IP_ADDRESS='127.0.0.1',
    db=DatabaseSettings(
        DATABASE_URL='postgresql+asyncpg://postgres:Lolipop!2009@localhost:5432/postgres',
        POOL_SIZE=500,
        MAX_OVERFLOW=100
    ),
    prefix=RoutersPrefix(
        AUTH='/v1/api/auth',

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

