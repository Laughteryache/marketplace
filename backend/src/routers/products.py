from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from fastapi.responses import JSONResponse

from core.config import settings
from core.schemes import TokenPayloadModel, BusinessUploadProductScheme, ProductGetScheme
from core.database.helper import db_helper

from core.database.functions import BusinessDB

from services.security import JWTAuth, get_payload_by_access_token

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    tags=["Products"],
    prefix=settings.prefix.PRODUCTS
)

@router.post('/')
async def create_new_product(
        creds: BusinessUploadProductScheme,
        token_payload: TokenPayloadModel = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if token_payload.role != 'business':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only for Business')
    categories = await BusinessDB.get_categories(session=session)
    if creds.category_id not in categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Category not found')
    product_id = await BusinessDB.create_product(
        creds=creds,
        business_id=int(token_payload.uid),
        session=session)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"product_id": product_id})

@router.get('/', 
            response_model=ProductGetScheme,
            response_model_exclude_none=True)
async def get_business_product(
        id: int,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    product_data = await BusinessDB.get_product(id, session)
    if not product_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found')
    return product_data
