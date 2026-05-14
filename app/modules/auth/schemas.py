from pydantic import BaseModel, Field

from app.modules.users.schemas import UserRead


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class ForgotPasswordRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)


class ForgotPasswordResponse(BaseModel):
    reset_token: str | None = None


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
