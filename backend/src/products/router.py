from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db_core.helper import db_helper
from typing_extensions import List

from .db import BusinessDB
from .models import BusinessUploadProductScheme, ProductGetScheme, CategoryModel

from global_dependencies import get_payload_by_access_token, TokenPayloadModel
from global_config import settings


router = APIRouter(
    tags=["products"],
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
    if creds.category_id not in await BusinessDB.get_categories_ids(session=session):
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

@router.get('/categories', response_model=List[CategoryModel] | CategoryModel)
async def get_all_categories(
        category_id: int | None = None,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> CategoryModel:
    category = await BusinessDB.get_categories(session=session, id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Category not found')
    return category