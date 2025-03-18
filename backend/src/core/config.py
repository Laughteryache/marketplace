from authx import AuthXConfig
from pydantic_settings import BaseSettings
from time import time
from loguru import logger
from datetime import timedelta


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str
    POOL_SIZE: int = 50
    MAX_OVERFLOW: int = 10

class RoutersPrefix(BaseSettings):
    USER_AUTH: str
    BUSINESS_AUTH: str
    USER_INTERFACE: str
    TOKEN_AUTH: str
    IMAGE_UPLOAD: str
    BUSINESS_PHOTOS: str

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
    jwt_tokens: AuthXConfig



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
        USER_AUTH='/v1/api/user/auth',
        BUSINESS_AUTH='/v1/api/business/auth',
        USER_INTERFACE='/v1/api/ui',
        TOKEN_AUTH='/v1/api/auth-utils',
        IMAGE_UPLOAD='/v1/api/images',
        BUSINESS_PHOTOS=''
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
    jwt_tokens=AuthXConfig(
        JWT_SECRET_KEY='SECRET_KEY',
        JWT_TOKEN_LOCATION=['cookies'],
        JWT_ACCESS_COOKIE_NAME='access_token',
        JWT_REFRESH_COOKIE_NAME='refresh_token',
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=30),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30),
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

