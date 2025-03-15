from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from core.database.functions import UsersDB
from core.database.helper import db_helper
from core.config import settings
from core.schemes import SignUpScheme, SignInScheme, TokenInfo
from services.security import JWTAuth


router = APIRouter(
    prefix=settings.prefix.USER_AUTH,
    tags=["User Authorization"]
)

@router.post('/sign-up')
async def user_sign_up(
        creds: SignUpScheme,
        response: Response,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if not await UsersDB.check_exists(session=session, creds=creds):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with provided login or email already exists.")
    uid = await UsersDB.register(session, creds)
    access_token = await JWTAuth.create_access(user_id=uid, token_for='user')
    refresh_token = await JWTAuth.create_refresh(user_id=uid, token_for='user')
    response.set_cookie(
        key=settings.jwt_tokens.JWT_ACCESS_COOKIE_NAME,
        value=access_token)
    response.set_cookie(
        key=settings.jwt_tokens.JWT_REFRESH_COOKIE_NAME,
        value=refresh_token)
    return TokenInfo(
        refresh_token=refresh_token,
        access_token=access_token
    )

@router.post('/sign-in')
async def user_sign_in(
        creds: SignInScheme,
        # response: Response,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
        if not await UsersDB.verify_password(session=session,
                                             creds=creds):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.")
        uid = await UsersDB.get_id(session=session,
                                        creds=creds)
        access_token = await JWTAuth.create_access(user_id=uid, token_for='user')
        refresh_token = await JWTAuth.create_refresh(user_id=uid, token_for='user')
        # response.set_cookie(
        #     key=settings.jwt_tokens.JWT_ACCESS_COOKIE_NAME,
        #     value=access_token)
        # response.set_cookie(
        #     key=settings.jwt_tokens.JWT_REFRESH_COOKIE_NAME,
        #     value=refresh_token)
        return TokenInfo(
            refresh_token=refresh_token,
            access_token=access_token
        )