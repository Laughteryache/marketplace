from authx import TokenPayload
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from global_config import settings
from global_dependencies import TokenPayloadModel, get_payload_by_access_token
from db_core.helper import db_helper

from .db import UsersDB

router = APIRouter(
    tags=['Orders'],
    prefix=settings.prefix.ORDER,
)


@router.get('/user/cart')
async def get_user_cart(
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if token_payload.role != 'user':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only users have shopping cart')
    user_cart = await UsersDB.get_cart(
        session=session,
        user_id=token_payload.uid,)
    if not user_cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Cart is empty or user doesn\'t exist')
    return user_cart

