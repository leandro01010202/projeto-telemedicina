from sqlalchemy.ext.asyncio import AsyncSession

from domains.auth.models import User, TipoUsuario
from domains.auth.schemas import UserCreate, UserUpdate, TokenResponse, UserResponse
from domains.auth.repository import UserRepository
from core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from core.config import get_settings
from core.exceptions import UnauthorizedException, NotFoundException, ValidationException

settings = get_settings()


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserRepository(db)

    async def register(self, data: UserCreate) -> TokenResponse:
        user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            nome=data.nome,
            tipo=data.tipo,
        )
        created_user = await self.repository.create(user)
        return await self._generate_tokens(created_user)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.repository.get_by_email(email)
        if not user:
            raise UnauthorizedException("Email ou senha incorretos")

        if not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Email ou senha incorretos")

        if not user.is_active:
            raise UnauthorizedException("Usuário desativado")

        return await self._generate_tokens(user)

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        try:
            payload = verify_refresh_token(refresh_token)
        except ValueError:
            raise UnauthorizedException("Refresh token inválido ou expirado")

        user_id = payload.get("sub")
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("Usuário não encontrado")

        if not user.is_active:
            raise UnauthorizedException("Usuário desativado")

        return await self._generate_tokens(user)

    async def get_user(self, user_id: int) -> UserResponse:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Usuário não encontrado")
        return UserResponse.model_validate(user)

    async def update_user(self, user_id: int, data: UserUpdate) -> UserResponse:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Usuário não encontrado")

        if data.email and data.email != user.email:
            existing = await self.repository.get_by_email(data.email)
            if existing:
                raise ValidationException("Email já está em uso")
            user.email = data.email

        if data.nome:
            user.nome = data.nome

        if data.password:
            user.hashed_password = get_password_hash(data.password)

        updated_user = await self.repository.update(user)
        return UserResponse.model_validate(updated_user)

    async def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Usuário não encontrado")

        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedException("Senha atual incorreta")

        user.hashed_password = get_password_hash(new_password)
        await self.repository.update(user)
        return True

    async def _generate_tokens(self, user: User) -> TokenResponse:
        token_data = {"sub": user.id, "email": user.email, "tipo": user.tipo.value}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse.model_validate(user),
        )
