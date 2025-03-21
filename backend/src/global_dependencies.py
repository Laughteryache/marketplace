from fastapi import File, UploadFile, HTTPException, Cookie, status
import string
import aiofiles
import random
from loguru import logger
from pydantic import BaseModel

from auth.utils import JWTAuth

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # ограничение 5 MB


class TokenPayloadModel(BaseModel):
    role: str
    uid: str

async def random_file_name() -> str:
    return ''.join(random.choices(string.ascii_letters, k=50))


async def get_payload_by_access_token(
        access_token: str = Cookie('access_token')
) -> HTTPException | TokenPayloadModel:
    token_payload = await JWTAuth.decode_token(access_token)
    if not token_payload or token_payload=='Token expired' or token_payload.type != 'access':
        raise HTTPException(status_code=401, detail="Invalid access token.")
    sub = token_payload.sub.split(':')
    if sub[0] not in ['user', 'business']:
        raise HTTPException(status_code=401, detail="Invalid access token.")
    try:
        int(sub[1])
        return TokenPayloadModel(uid=sub[1], role=sub[0])
    except ValueError:
        logger.critical(f"SECURITY ALERT: role:{sub[0]} uid:{sub[1]}")
        raise HTTPException(status_code=401, detail="Invalid access token.")


async def check_uploaded_file(
        file: UploadFile = File(...)
) -> str | HTTPException:
    filename = file.filename
    file_extension = filename[filename.rfind("."):].lower()  # Получаем расширение файла
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_extension!r}. Allowed formats are {ALLOWED_EXTENSIONS}")
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024} MB.")
    try:
        new_file_name = await random_file_name()
        new_file_path = f"uploaded_files/{new_file_name}{file_extension}"
        content = await file.read()
        async with aiofiles.open(new_file_path, "wb") as f:
            await f.write(content)
        return f'{new_file_name}{file_extension}'
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))