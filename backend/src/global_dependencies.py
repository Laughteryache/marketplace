from fastapi import HTTPException, Cookie, status
from auth.utils import JWTAuth
from loguru import logger
from pydantic import BaseModel

class TokenPayloadModel(BaseModel):
    role: str
    uid: str

@logger.catch
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
