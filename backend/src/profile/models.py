import re
import datetime
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator, Field






class BusinessProfileScheme(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=500)
    location: str = Field(min_length=1, max_length=90)
