from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession

from secrets import compare_digest
import time

from src.core.database.helper import db_helper
from src.core.config import settings
from src.core.schemes import UserSignUpScheme, UserSignInScheme

router = APIRouter(
    prefix=settings.prefix.USER_AUTH,
    tags=["User Authorization"]
)

@router.post('/sign-up')
async def user_sign_up(
        creds: UserSignUpScheme,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    pass


@router.post('/sign-in')
async def user_sign_in(
        creds: UserSignInScheme,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    pass
    # Я в зал ушел