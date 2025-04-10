from fastapi import APIRouter, Depends, HTTPException, status, Cookie, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import List

from backend.src.db_core.helper import db_helper
from backend.src.cloud.file_uploader import delete_file, get_new_avatar_id

from backend.src.products.db import BusinessDB
from backend.src.products.models import BusinessUploadProductScheme, ProductGetScheme, CategoryModel

from backend.src.global_dependencies import get_payload_by_access_token, TokenPayloadModel, check_uploaded_file
from backend.src.global_config import settings


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


@router.get('/search', response_model=List[ProductGetScheme])
async def search_business_product(
    name: str,
    start_id: int | None = None,
    session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if start_id:
        products = await BusinessDB.search_product(name=name,
                                                   start_id=start_id,
                                                   session=session)
    else:
        products = await BusinessDB.search_product(name=name,
                                                   start_id=1,
                                                   session=session)
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Product not found')
    return products

@router.get('/image')
async def get_product_image(
        product_id: int,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    product = await BusinessDB.get_product(id=product_id, session=session)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found')
    if not product.logo_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product image not found'
        )
    return {"file_link": f"https://drive.google.com/file/d/{product.logo_path}/preview"}
@router.put('/image')
async def upload_business_product_image(
        product_id: int,
        session: AsyncSession = Depends(db_helper.get_async_session),
        token_payload: TokenPayloadModel = Depends(get_payload_by_access_token),
        picture_name: UploadFile = Depends(check_uploaded_file)
) -> JSONResponse:
    if token_payload.role != 'business':
        await delete_file(picture_name)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only for Business')

    product_data = await BusinessDB.get_product(id=product_id, session=session)

    if not product_data:
        await delete_file(picture_name)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found')

    if int(product_data.creator_id) != int(token_payload.uid):
        await delete_file(picture_name)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="It's not your product")
    file_id = await get_new_avatar_id(picture_name)
    await BusinessDB.save_product_image_id(
        product_id=product_id,
        session=session,
        file_id=file_id)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "file_link": f"https://drive.google.com/file/d/{file_id}/preview"
        }
    )

@router.get('/products/profile')
async def get_all_business_products(
        id: int,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    products = await BusinessDB.get_business_products(id=id, session=session)
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This Business haven\'t any products or not exist\'s')
    return products