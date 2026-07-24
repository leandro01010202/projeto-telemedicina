from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domains.pacientes.models import Paciente, Alergia, Comorbidade
from core.exceptions import NotFoundException, ConflictException


class PacienteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, paciente_id: int) -> Paciente | None:
        result = await self.db.execute(
            select(Paciente)
            .where(Paciente.id == paciente_id)
            .options(selectinload(Paciente.alergias), selectinload(Paciente.comorbidades))
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Paciente | None:
        result = await self.db.execute(
            select(Paciente)
            .where(Paciente.user_id == user_id)
            .options(selectinload(Paciente.alergias), selectinload(Paciente.comorbidades))
        )
        return result.scalar_one_or_none()

    async def get_by_cpf(self, cpf: str) -> Paciente | None:
        result = await self.db.execute(
            select(Paciente).where(Paciente.cpf == cpf)
        )
        return result.scalar_one_or_none()

    async def create(self, paciente: Paciente) -> Paciente:
        existing = await self.get_by_cpf(paciente.cpf)
        if existing:
            raise ConflictException("CPF já cadastrado")

        self.db.add(paciente)
        await self.db.flush()
        await self.db.refresh(paciente)
        return paciente

    async def update(self, paciente: Paciente) -> Paciente:
        await self.db.flush()
        await self.db.refresh(paciente)
        return paciente

    async def delete(self, paciente_id: int) -> None:
        paciente = await self.get_by_id(paciente_id)
        if not paciente:
            raise NotFoundException("Paciente não encontrado")
        await self.db.delete(paciente)

    async def search(
        self,
        query: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Paciente], int]:
        stmt = select(Paciente).options(
            selectinload(Paciente.alergias),
            selectinload(Paciente.comorbidades)
        )

        if query:
            search_filter = or_(
                Paciente.cpf.ilike(f"%{query}%"),
            )
            stmt = stmt.where(search_filter)

        # Count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Results
        stmt = stmt.offset(skip).limit(limit).order_by(Paciente.created_at.desc())
        result = await self.db.execute(stmt)
        pacientes = list(result.scalars().all())

        return pacientes, total

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Paciente]:
        result = await self.db.execute(
            select(Paciente)
            .offset(skip)
            .limit(limit)
            .order_by(Paciente.created_at.desc())
        )
        return list(result.scalars().all())

    # Alergias
    async def add_alergia(self, paciente_id: int, alergia: Alergia) -> Alergia:
        paciente = await self.get_by_id(paciente_id)
        if not paciente:
            raise NotFoundException("Paciente não encontrado")

        self.db.add(alergia)
        await self.db.flush()
        await self.db.refresh(alergia)
        return alergia

    async def remove_alergia(self, alergia_id: int) -> None:
        result = await self.db.execute(select(Alergia).where(Alergia.id == alergia_id))
        alergia = result.scalar_one_or_none()
        if not alergia:
            raise NotFoundException("Alergia não encontrada")
        await self.db.delete(alergia)

    # Comorbidades
    async def add_comorbidade(self, paciente_id: int, comorbidade: Comorbidade) -> Comorbidade:
        paciente = await self.get_by_id(paciente_id)
        if not paciente:
            raise NotFoundException("Paciente não encontrado")

        self.db.add(comorbidade)
        await self.db.flush()
        await self.db.refresh(comorbidade)
        return comorbidade

    async def remove_comorbidade(self, comorbidade_id: int) -> None:
        result = await self.db.execute(select(Comorbidade).where(Comorbidade.id == comorbidade_id))
        comorbidade = result.scalar_one_or_none()
        if not comorbidade:
            raise NotFoundException("Comorbidade não encontrada")
        await self.db.delete(comorbidade)
