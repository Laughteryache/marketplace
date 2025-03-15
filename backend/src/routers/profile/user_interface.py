from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.schemes import TokenPayloadModel

from services.security import JWTAuth, get_payload_by_access_token

from core.database.functions import UsersDB, BusinessDB
from core.database.helper import db_helper


router = APIRouter(
    prefix=settings.prefix.USER_INTERFACE,
    tags=["User Interface"]
)

class BalanceInfo(BaseModel):
    balance: int


@router.get('/balance')
async def get_user_balance(
        token_payload: TokenPayloadModel = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if token_payload.role == 'user':
        user_id = token_payload.uid
        user_balance = await UsersDB.get_balance(user_id=user_id, session=session)
        return BalanceInfo(balance=user_balance)
    elif token_payload.role == 'business':
        business_id = token_payload.uid
        business_balance = await BusinessDB.get_balance(business_id=business_id, session=session)
        return BalanceInfo(balance=business_balance)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.")