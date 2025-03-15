from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from secrets import compare_digest


from core.database.functions import BusinessDB
from core.database.helper import db_helper
from core.config import settings
from core.schemes import SignUpScheme, SignInScheme
from services.security import JWTAuth

router = APIRouter(
    prefix=settings.prefix.BUSINESS_AUTH,
    tags=["Business Authorization"]
)

@router.post('/sign-up')
async def business_sign_up(
        creds: SignUpScheme,
        response: Response,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if not await BusinessDB.check_exists(session, creds):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Business with provided login or email already exists.")
    business_id = await BusinessDB.register(session, creds)
    access_token = await JWTAuth.create_access(user_id=business_id, token_for='business')
    refresh_token = await JWTAuth.create_refresh(user_id=business_id, token_for='business')
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
async def business_sign_in(
        creds: SignInScheme,
        response: Response,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if not await BusinessDB.verify_password(session=session,
                                             creds=creds):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
    business_id = await BusinessDB.get_id(creds=creds,
                                          session=session)
    access_token = await JWTAuth.create_access(user_id=business_id, token_for='business')
    refresh_token = await JWTAuth.create_refresh(user_id=business_id, token_for='business')
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