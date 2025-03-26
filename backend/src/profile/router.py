from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from global_dependencies import TokenPayloadModel, get_payload_by_access_token, check_uploaded_file
from global_config import settings

from cloud.file_uploader import get_new_avatar_id, delete_file
from db_core.helper import db_helper

from .db import BusinessDB, UsersDB
from .models import BusinessProfileScheme, ProfileInfo
from .utils import convert_to_ekb_time

router = APIRouter(
    tags=["profile"],
    prefix=settings.prefix.PROFILE,
)

@router.put('/business/image')
async def upload_business_image(
        token_payload: TokenPayloadModel = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session),
        picture_name: UploadFile = Depends(check_uploaded_file)
) -> JSONResponse:
    if token_payload.role != 'business':
        await delete_file(picture_name)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only for Business')
    file_id = await get_new_avatar_id(picture_name)
    await BusinessDB.save_avatar_id(
        file_id=file_id,
        session=session,
        business_id=token_payload.uid)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "file_link": f"https://drive.google.com/file/d/{file_id}/preview"
        }
    )

@router.get('/business/image')
async def get_business_image(
        id: str,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    avatar_id = await BusinessDB.get_profile(id, session)
    if not avatar_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    if avatar_id.logo_id:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "file_link": f"https://drive.google.com/file/d/{avatar_id.logo_id}/preview"
            }
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Image not found'
    )


@router.get('/balance')
async def get_user_balance(
        token_payload: TokenPayloadModel = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if token_payload.role == 'user':
        return {'balance': await UsersDB.get_balance(user_id=token_payload.uid, session=session)}
    elif token_payload.role == 'business':
        return {'balance': await BusinessDB.get_balance(business_id=token_payload.uid, session=session)}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.")


@router.patch('/business')
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

@router.get('/business', response_model=ProfileInfo, response_model_exclude_none=True)
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