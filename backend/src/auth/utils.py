from authx import AuthX, TokenPayload
from argon2 import PasswordHasher
from loguru import logger

from backend.src.auth.config import authx_config

ph = PasswordHasher()
authx_security = AuthX(config=authx_config)

class JWTAuth:

    @staticmethod
    @logger.catch
    async def create_access(user_id: str, token_for: str) -> str:
        return authx_security.create_access_token(uid=f'{token_for}:{user_id}')

    @staticmethod
    @logger.catch
    async def create_refresh(user_id: str, token_for: str) -> str:
        return authx_security.create_refresh_token(uid=f'{token_for}:{user_id}')

    @staticmethod
    @logger.catch
    async def decode_token(token: str) -> TokenPayload:
        try:
            return authx_security._decode_token(token=token)
        except:
            return 'Token expired'


class HashSecurity:

    @staticmethod
    @logger.catch
    async def get_hash(message: str) -> str:
        return ph.hash(message)

    @staticmethod
    @logger.catch
    async def verify_hash(message: str, hashed_message: str) -> bool:
        try:
            return ph.verify(hashed_message, message)
        except:
            return False