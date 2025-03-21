import re
import datetime
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator, Field



class BusinessUploadProductScheme(BaseModel):
    name: str = Field(min_length=5, max_length=50)
    description: str = Field(min_length=10, max_length=500)
    category_id: int
    price: int = Field(ge=1)
    sex: str
    adult_only: bool
    start_date: datetime.date # The start date of the product availability in YYYY-MM-DD format.
    end_date: datetime.date | None = None
    quanity: int = Field(ge=1)

    @field_validator("sex", check_fields=False)
    def validate_gender(cls, sex: str):
        if sex not in ['m', 'f', 'u']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Only 2 genders are allowed: m - for male, f - for female. And u - Unisex for 2 genders')
        return sex

class ProductGetScheme(BaseModel):
    product_id: int
    name: str
    description: str
    logo_path: str | None = None
    category_id: int
    price: int
    sex: str
    adult_only: bool
    start_date: str
    end_date: str | None = None
    quanity: int
    creator_id: int

class CategoryModel(BaseModel):
    category_id: int
    name: str
    description: str