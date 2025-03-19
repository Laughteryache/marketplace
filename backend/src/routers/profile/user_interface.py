from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.schemes import TokenPayloadModel, BusinessProfileScheme

from services.time_converter import convert_to_ekb_time
from services.security import JWTAuth, get_payload_by_access_token

from core.database.functions import UsersDB, BusinessDB
from core.database.helper import db_helper


router = APIRouter(
    prefix=settings.prefix.USER_INTERFACE,
    tags=["User Interface"]
)

class BalanceInfo(BaseModel):
    balance: int


@router.get('/ui/balance')
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


@router.patch('/business/profile/')
async def patch_business_profile(
        creds: BusinessProfileScheme,
        token_payload: TokenPayloadModel = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if token_payload.role != 'business':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only for Business'
        )
    await BusinessDB.update_profile(
        creds=creds,
        business_id=token_payload.uid,
        session=session)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Profile updated successfully."
        }
    )

class ProfileInfo(BaseModel):
    id: int
    title: str
    description: str
    file_link: str = None
    location: str
    date_joined: str

@router.get('/business/profile/', response_model=ProfileInfo, response_model_exclude_none=True)
async def get_business_profile(
        id: int,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    profile = await BusinessDB.get_profile(id=id, session=session)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Profile not found')
    date_joined = await convert_to_ekb_time(profile.date_joined)
    logo_id = profile.logo_id
    if logo_id:
        return ProfileInfo(
            id=id,
            title=profile.title,
            description=profile.description,
            file_link=f"https://drive.google.com/file/d/{logo_id}/preview",
            location=profile.location,
            date_joined=f"{date_joined}")
    return ProfileInfo(
        id=id,
        title=profile.title,
        description=profile.description,
        location=profile.location,
        date_joined=f"{date_joined}")