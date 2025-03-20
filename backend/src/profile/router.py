
router = APIRouter()

@router.post('/')
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

@router.get('/')
async def get_business_image(
        id: str,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    avatar_id = await BusinessDB.get_profile(id, session)
    if avatar_id:
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