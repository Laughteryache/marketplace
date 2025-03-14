import re
from pydantic import BaseModel, EmailStr, field_validator


class UserSignUpScheme(BaseModel):
    login: str
    email: EmailStr
    password: str

    @field_validator("password", check_fields=False)
    def validate_password(cls, password: str):
        if not re.fullmatch(
                r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+|\\}{:;'\"><?/,.]).{8,}$", password):
            raise ValueError
        return password

class UserSignInScheme(BaseModel):
    login: str | None = None
    email: EmailStr | None = None
    password: str

class BusinessSignUpScheme(BaseModel):
    pass

class BusinessSignInScheme(BaseModel):
    login: str | None = None
    email: EmailStr | None = None
    password: str
