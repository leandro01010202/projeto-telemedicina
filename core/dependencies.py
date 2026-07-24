from typing import Optional
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import verify_access_token
from core.exceptions import UnauthorizedException
from domains.auth.models import User
from domains.auth.repository import UserRepository


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization:
        raise UnauthorizedException("Token de acesso não fornecido")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise UnauthorizedException("Esquema de autenticação inválido")
    except ValueError:
        raise UnauthorizedException("Formato de token inválido")

    try:
        payload = verify_access_token(token)
        user_id: int = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Token inválido")
    except ValueError as e:
        raise UnauthorizedException(str(e))

    repository = UserRepository(db)
    user = await repository.get_by_id(user_id)
    if not user:
        raise UnauthorizedException("Usuário não encontrado")

    return user


def require_role(*roles: str):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.tipo not in roles:
            raise UnauthorizedException(f"Permissão requerida: {', '.join(roles)}")
        return current_user
    return role_checker


get_current_admin = require_role("admin")
get_current_medico = require_role("admin", "medico")
get_current_medico_only = require_role("medico")
