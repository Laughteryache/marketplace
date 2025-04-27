from authx import TokenPayload
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.db_core.helper import db_helper
from backend.src.global_config import settings
from backend.src.global_dependencies import get_payload_by_access_token
from backend.src.orders.db import UsersDB

router = APIRouter(
    tags=['orders'],
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
        user_id=token_payload.uid, )
    if not user_cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Cart is empty or user doesn\'t exist')
    return user_cart


@router.delete('/user/cart')
async def drop_user_cart(
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if token_payload.role != 'user':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Only users have shopping cart')
    await UsersDB.drop_cart_items(session=session, user_id=token_payload.uid, )
    return {'status': 'ok'}


@router.post('/user/cart/{product_id}/delete')
async def drop_item_in_cart(
        product_id: int,
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if token_payload.role != 'user':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Only users have shopping cart')
    if not await UsersDB.drop_cart_item(session=session,
                                        user_id=token_payload.uid,
                                        product_id=product_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Item not in cart')
    return {'status': 'ok'}


@router.post('/user/cart/{product_id}/add')
async def add_item_to_cart(
        product_id: int,
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if token_payload.role != 'user':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Only users have shopping cart')
    await UsersDB.add_cart_item(session=session, product_id=product_id,
                                user_id=token_payload.uid)
    return {'status': 'ok'}

@router.post('/user/order/begin')
async def begin_order(
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if token_payload.role != 'user':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Only users have shopping cart')
    cart_state = await UsersDB.check_cart(
        session=session,
        user_id=int(token_payload.uid))
    if cart_state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User doesn\'t exists')
    if cart_state is False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Cart is empty')
    if cart_state is True:
        cart = await UsersDB.get_cart(session=session, user_id=int(token_payload.uid))
        cart_price = await UsersDB.check_balance(session=session, user_id=int(token_payload.uid), cart=cart)
        product_quanity = await UsersDB.check_quanity(session=session, cart=cart)

        if product_quanity is not True:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    'message': 'Available quanity smaller',
                    'product_id': product_quanity[0],
                    'quanity_different': product_quanity[1]
                }
            )
        if not cart_price:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Cart price bigger than balance')
        order_id = await UsersDB.register_order(session=session, user_id=int(token_payload.uid), cart_price=cart_price)
        if order_id:
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={'order_id': order_id})


