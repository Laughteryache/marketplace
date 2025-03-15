import re
from pydantic import BaseModel, EmailStr, field_validator, Field


class SignUpScheme(BaseModel):
    login: str = Field(min_length=4,max_length=25)
    email: EmailStr
    password: str = Field(max_length=40)

    @field_validator("password", check_fields=False)
    def validate_password(cls, password: str):
        if not re.fullmatch(
                r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+|\\}{:;'\"><?/,.]).{8,}$", password):
            raise ValueError
        return password

class SignInScheme(BaseModel):
    email: EmailStr
    password: str = Field(max_length=40)
