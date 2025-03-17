from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from core.database.helper import db_helper
from core.database.functions import UsersDB, BusinessDB

from core.schemes import TokenInfo
from core.config import settings
from services.security import JWTAuth

router = APIRouter(
    prefix=settings.prefix.TOKEN_AUTH,
    tags=["Token Utils"]
)


@router.get("/refresh",
            response_model=TokenInfo,
            response_model_exclude_unset=True)

async def refresh_access_token(
        refresh_token: str = Cookie('refresh_token'),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    token_payload = await JWTAuth.decode_token(refresh_token)
    if not token_payload or token_payload=='Token expired' or token_payload.type != 'refresh':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.")
    sub = token_payload.sub.split(':')
    try:
        token_owner = sub[0]
        uid = sub[1]
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.")
    if token_owner == 'user':
        user_data = await UsersDB.get_data_by_id(user_id = uid, session=session)
        if not user_data or user_data.is_deleted is True:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account not founded.")
    elif token_owner == 'business':
        user_data = await BusinessDB.get_data_by_id(business_id = uid, session=session)
        if not user_data or user_data.is_deleted is True:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Business account not founded.")
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.")

    access_token = await JWTAuth.create_access(user_id=uid, token_for=token_owner)
    return TokenInfo(
        access_token=access_token
    )