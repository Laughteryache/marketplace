from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.auth.db import BusinessDB, UsersDB
from backend.src.auth.models import SignUpScheme, SignInScheme
from backend.src.auth.utils import JWTAuth
from backend.src.db_core.helper import db_helper
from backend.src.global_config import settings
from backend.src.global_dependencies import get_payload_by_access_token

router = APIRouter(
    prefix=settings.prefix.AUTH,
    tags=["auth"]
)


@router.post('/business/sign-up')
async def business_sign_up(
        response: Response,
        creds: SignUpScheme,
        session: AsyncSession = Depends(db_helper.get_async_session),
) -> JSONResponse:
    if not await BusinessDB.check_exists(session, creds):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Business with provided email already exists.")

    business_id = await BusinessDB.register(session, creds)
    access_token = await JWTAuth.create_access(user_id=business_id, token_for='business')
    refresh_token = await JWTAuth.create_refresh(user_id=business_id, token_for='business')

    response.set_cookie("access_token", access_token, httponly=True)
    response.set_cookie("refresh_token", refresh_token, httponly=True)

    return {
        "business_id": business_id,
        'access_token': access_token,
        'refresh_token': refresh_token
    }


@router.post('/business/sign-in')
async def business_sign_in(
        response: Response,
        creds: SignInScheme,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if not await BusinessDB.verify_password(session=session,
                                            creds=creds):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.")

    business_id = await BusinessDB.get_id(creds=creds,
                                          session=session)

    access_token = await JWTAuth.create_access(user_id=business_id, token_for='business')
    refresh_token = await JWTAuth.create_refresh(user_id=business_id, token_for='business')

    response.set_cookie("access_token", access_token, httponly=True)
    response.set_cookie("refresh_token", refresh_token, httponly=True)

    return {
        "business_id": business_id,
        'access_token': access_token,
        'refresh_token': refresh_token
    }


@router.post('/user/sign-up')
async def user_sign_up(
        response: Response,
        creds: SignUpScheme,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if not await UsersDB.check_exists(session=session, creds=creds):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with provided email already exists.")
    uid = await UsersDB.register(session, creds)
    access_token = await JWTAuth.create_access(user_id=uid, token_for='user')
    refresh_token = await JWTAuth.create_refresh(user_id=uid, token_for='user')

    response.set_cookie("access_token", access_token, httponly=True)
    response.set_cookie("refresh_token", refresh_token, httponly=True)

    return {
        'user_id': uid,
        'access_token': access_token,
        'refresh_token': refresh_token
    }


@router.post('/user/sign-in')
async def user_sign_in(
        response: Response,
        creds: SignInScheme,
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

    response.set_cookie("access_token", access_token, httponly=True)
    response.set_cookie("refresh_token", refresh_token, httponly=True)

    return {
        'user_id': uid,
        'access_token': access_token,
        'refresh_token': refresh_token
    }


@router.get('/me')
async def get_user_info(
        token_payload: JWTAuth = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session),
) -> JSONResponse:
    role = None
    if token_payload.role == 'user':
        user_data = await UsersDB.get_data_by_id(user_id=token_payload.uid,
                                                 session=session)
        role = user_data.role
    elif token_payload.role == 'business':
        user_data = await BusinessDB.get_data_by_id(business_id=token_payload.uid,
                                                    session=session)
        role = 'business'
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if user_data.is_deleted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return {
        'id': user_data.id,
        'role': role,
        'email': user_data.email,
    }


@router.get("/refresh-token")
async def refresh_access_token(
        response: Response,
        refresh_token: str = Cookie('refresh_token'),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    token_payload = await JWTAuth.decode_token(refresh_token)
    if not token_payload or token_payload == 'Token expired' or token_payload.type != 'refresh':
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

    if type(uid) != str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token."
        )

    if token_owner == 'user':
        try:
            user_data = await UsersDB.get_data_by_id(user_id=uid, session=session)
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account not founded."
            )
        if not user_data or user_data.is_deleted is True:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account not founded.")
    elif token_owner == 'business':
        try:
            user_data = await BusinessDB.get_data_by_id(business_id=uid, session=session)
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Business account not founded."
            )
        if not user_data or user_data.is_deleted is True:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Business account not founded.")
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.")

    access_token = await JWTAuth.create_access(user_id=uid, token_for=token_owner)
    response.set_cookie("access_token", access_token, httponly=True)
    return {'access_token': access_token}
