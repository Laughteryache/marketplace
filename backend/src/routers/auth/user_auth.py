from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from secrets import compare_digest
import time

from core.database.functions import UsersDB
from core.database.helper import db_helper
from core.config import settings
from core.schemes import UserSignUpScheme, UserSignInScheme
from services.security import JWTAuth
from sqlalchemy.ext.horizontal_shard import set_shard_id

router = APIRouter(
    prefix=settings.prefix.USER_AUTH,
    tags=["User Authorization"]
)

@router.post('/sign-up')
async def user_sign_up(
        creds: UserSignUpScheme,
        #response: Response,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if not await UsersDB.check_exists(session, creds.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with provided login or email already exists.")
    uid = await UsersDB.register(session, creds)
    access_token = await JWTAuth.create_access(user_id=uid)
    refresh_token = await JWTAuth.create_refresh(user_id=uid)
    # response.set_cookie(
    #     key=settings.jwt_tokens.JWT_ACCESS_COOKIE_NAME,
    #     value=access_token)
    # response.set_cookie(
    #     key=settings.jwt_tokens.JWT_REFRESH_COOKIE_NAME,
    #     value=refresh_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@router.post('/sign-in')
async def user_sign_in(
        creds: UserSignInScheme,
        # response: Response,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
        if not await UsersDB.verify_password(session=session,
                                             creds=creds):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login or password.")
        uid = await UsersDB.get_id(session=session,
                                        creds=creds)
        access_token = await JWTAuth.create_access(user_id=uid)
        refresh_token = await JWTAuth.create_refresh(user_id=uid)
        # response.set_cookie(
        #     key=settings.jwt_tokens.JWT_ACCESS_COOKIE_NAME,
        #     value=access_token)
        # response.set_cookie(
        #     key=settings.jwt_tokens.JWT_REFRESH_COOKIE_NAME,
        #     value=refresh_token)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }