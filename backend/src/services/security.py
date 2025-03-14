import asyncio

from authx import AuthX, TokenPayload
from src.core.config import settings
from loguru import logger

authx_security = AuthX(config=settings.jwt_tokens)

class JWTAuth:

    @staticmethod
    @logger.catch
    async def create_access(user_id: str) -> str:
        return authx_security.create_access_token(uid=str(user_id))

    @staticmethod
    @logger.catch
    async def create_refresh(user_id: str) -> str:
        return authx_security.create_refresh_token(uid=str(user_id))

    @staticmethod
    @logger.catch
    async def decode_token(token: str) -> TokenPayload:
        try:
            return authx_security._decode_token(token=token)
        except:
            return 'Token expired'
