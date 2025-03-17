from fastapi import APIRouter, Depends, HTTPException, status, Cookie, UploadFile
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.schemes import TokenPayloadModel

from services.security import JWTAuth, get_payload_by_access_token, check_uploaded_file

from core.database.functions import BusinessDB
from core.database.helper import db_helper
from core.cloud.avatar_upload import get_new_avatar_id

router = APIRouter(
    prefix=settings.prefix.IMAGE_UPLOAD,
    tags=["Images"]
)

@router.post('/upload')
async def upload_business_image(
        token_payload: TokenPayloadModel = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session),
        picture_name: UploadFile = Depends(check_uploaded_file)
) -> JSONResponse:
    if token_payload.role != 'business':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only for Business')
    file_id = await get_new_avatar_id(picture_name)
    await BusinessDB.save_avatar_id(
        file_id=file_id,
        session=session,
        business_id=token_payload.uid
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "file_link": f"https://drive.google.com/file/d/{file_id}/preview"
        }
    )