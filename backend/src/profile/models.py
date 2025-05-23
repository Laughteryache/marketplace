from pydantic import BaseModel, Field


class ProfileInfo(BaseModel):
    id: int
    title: str
    description: str
    file_link: str = None
    location: str
    date_joined: str


class BusinessProfileScheme(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1, max_length=500)
    location: str = Field(min_length=1, max_length=90)
