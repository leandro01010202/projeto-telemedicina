from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domains.receitas.models import Receita, ItemReceita, Atestado
from core.exceptions import NotFoundException


class ReceitaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, receita_id: int) -> Receita | None:
        result = await self.db.execute(
            select(Receita)
            .where(Receita.id == receita_id)
            .options(selectinload(Receita.itens))
        )
        return result.scalar_one_or_none()

    async def create(self, receita: Receita) -> Receita:
        self.db.add(receita)
        await self.db.flush()
        await self.db.refresh(receita)
        return receita

    async def sign(self, receita_id: int, signature_hash: str) -> Receita:
        receita = await self.get_by_id(receita_id)
        if not receita:
            raise NotFoundException("Receita não encontrada")

        receita.esta_assinada = True
        receita.assinatura_hash = signature_hash
        await self.db.flush()
        await self.db.refresh(receita)
        return receita

    async def list_by_paciente(self, paciente_id: int, include_expired: bool = False) -> list[Receita]:
        stmt = select(Receita).where(Receita.paciente_id == paciente_id)

        if not include_expired:
            expiry_date = datetime.now() - timedelta(days=365)  # Padrão: 1 ano
            stmt = stmt.where(Receita.created_at >= expiry_date)

        stmt = stmt.options(selectinload(Receita.itens)).order_by(Receita.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class AtestadoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, atestado_id: int) -> Atestado | None:
        result = await self.db.execute(
            select(Atestado).where(Atestado.id == atestado_id)
        )
        return result.scalar_one_or_none()

    async def create(self, atestado: Atestado) -> Atestado:
        self.db.add(atestado)
        await self.db.flush()
        await self.db.refresh(atestado)
        return atestado

    async def sign(self, atestado_id: int, signature_hash: str) -> Atestado:
        atestado = await self.get_by_id(atestado_id)
        if not atestado:
            raise NotFoundException("Atestado não encontrado")

        atestado.esta_assinado = True
        atestado.assinatura_hash = signature_hash
        await self.db.flush()
        await self.db.refresh(atestado)
        return atestado

    async def list_by_paciente(self, paciente_id: int) -> list[Atestado]:
        result = await self.db.execute(
            select(Atestado)
            .where(Atestado.paciente_id == paciente_id)
            .order_by(Atestado.created_at.desc())
        )
        return list(result.scalars().all())
