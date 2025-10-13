
from pydantic import BaseModel, Field

class UserAuth(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str = Field(alias='nome')
    email: str
    cargo: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class Token(BaseModel):
    access_token: str
    token_type: str
