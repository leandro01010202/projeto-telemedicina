from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from domains.auth.models import TipoUsuario


class UserBase(BaseModel):
    email: EmailStr
    nome: str = Field(..., min_length=2, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    tipo: TipoUsuario = TipoUsuario.PACIENTE


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    nome: str | None = Field(None, min_length=2, max_length=255)
    password: str | None = Field(None, min_length=8, max_length=100)


class UserResponse(UserBase):
    id: int
    tipo: TipoUsuario
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
