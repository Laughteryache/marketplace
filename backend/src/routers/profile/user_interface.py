from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from services.security import JWTAuth


router = APIRouter(
    prefix=settings.prefix.USER_INTERFACE,
    tags=["User Interface"]
)



@router.get('/balance')
async def get_user_balance(
        response: Response,
        access_token: ...,
        refresh_token: ...,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    pass