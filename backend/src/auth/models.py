import re
import datetime
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator, Field



class SignUpScheme(BaseModel):
    email: EmailStr
    password: str = Field(max_length=40)

    @field_validator("password", check_fields=False)
    def validate_password(cls, password: str):
        if not re.fullmatch(
                r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+|\\}{:;'\"><?/,.]).{8,}$", password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Password must be at least 8 characters long'
                       ' and include at least one uppercase letter,'
                       ' one lowercase letter, one digit,'
                       ' and one special character.')
        return password

class SignInScheme(BaseModel):
    email: EmailStr
    password: str = Field(max_length=40)

class TokenInfoScheme(BaseModel):
    access_token: str
    refresh_token: str | None = None

