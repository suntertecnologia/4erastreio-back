from pydantic import BaseModel, Field, EmailStr


class UserAuth(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    username: str = Field(alias="nome")
    email: EmailStr
    cargo: str
    is_active: bool

    class Config:
        from_attributes = True
        populate_by_name = True


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
