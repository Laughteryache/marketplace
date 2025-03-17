import asyncio
import random
import string
from argon2 import PasswordHasher
from authx import AuthX, TokenPayload
from core.config import settings
from fastapi import Cookie, HTTPException, UploadFile, File
from loguru import logger
from core.schemes import TokenPayloadModel
import aiofiles

authx_security = AuthX(config=settings.jwt_tokens)
ph = PasswordHasher()

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
        try: return ph.verify(hashed_message, message)
        except: return False

async def get_payload_by_access_token(
        access_token: str = Cookie('access_token')
) -> HTTPException | str:
    token_payload = await JWTAuth.decode_token(access_token)
    if not token_payload or token_payload=='Token expired' or token_payload.type != 'access':
        raise HTTPException(status_code=401, detail="Invalid access token.")
    sub = token_payload.sub.split(':')
    if sub[0] not in ['user', 'business']:
        raise HTTPException(status_code=401, detail="Invalid access token.")
    return TokenPayloadModel(uid=sub[1], role=sub[0])

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # ограничение 5 MB

async def random_file_name() -> str:
    return ''.join(random.choices(string.ascii_letters, k=50))

async def check_uploaded_file(
        file: UploadFile = File(...)
) -> str | HTTPException:
    filename = file.filename
    file_extension = filename[filename.rfind("."):].lower()  # Получаем расширение файла
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_extension}. Allowed formats are {ALLOWED_EXTENSIONS}")
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024} MB.")

    try:
        new_file_name = await random_file_name()
        new_file_path = f"src/uploaded_files/{new_file_name}{file_extension}"
        content = await file.read()
        async with aiofiles.open(new_file_path, "wb") as f:
            await f.write(content)

        return f'{new_file_name}{file_extension}'
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

