from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domains.medicos.models import Medico, Especialidade, AgendaMedico
from core.exceptions import NotFoundException, ConflictException


class MedicoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, medico_id: int) -> Medico | None:
        result = await self.db.execute(
            select(Medico)
            .where(Medico.id == medico_id)
            .options(selectinload(Medico.especialidade), selectinload(Medico.agenda))
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Medico | None:
        result = await self.db.execute(
            select(Medico)
            .where(Medico.user_id == user_id)
            .options(selectinload(Medico.especialidade), selectinload(Medico.agenda))
        )
        return result.scalar_one_or_none()

    async def get_by_crm(self, crm: str) -> Medico | None:
        result = await self.db.execute(select(Medico).where(Medico.crm == crm))
        return result.scalar_one_or_none()

    async def get_by_cpf(self, cpf: str) -> Medico | None:
        result = await self.db.execute(select(Medico).where(Medico.cpf == cpf))
        return result.scalar_one_or_none()

    async def create(self, medico: Medico) -> Medico:
        existing_crm = await self.get_by_crm(medico.crm)
        if existing_crm:
            raise ConflictException("CRM já cadastrado")

        existing_cpf = await self.get_by_cpf(medico.cpf)
        if existing_cpf:
            raise ConflictException("CPF já cadastrado")

        self.db.add(medico)
        await self.db.flush()
        await self.db.refresh(medico)
        return medico

    async def update(self, medico: Medico) -> Medico:
        await self.db.flush()
        await self.db.refresh(medico)
        return medico

    async def delete(self, medico_id: int) -> None:
        medico = await self.get_by_id(medico_id)
        if not medico:
            raise NotFoundException("Médico não encontrado")
        await self.db.delete(medico)

    async def search(
        self,
        query: str | None = None,
        especialidade_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Medico], int]:
        stmt = select(Medico).where(Medico.is_ativo == True).options(
            selectinload(Medico.especialidade)
        )

        if query:
            stmt = stmt.where(
                or_(
                    Medico.crm.ilike(f"%{query}%"),
                    Medico.cpf.ilike(f"%{query}%"),
                )
            )

        if especialidade_id:
            stmt = stmt.where(Medico.especialidade_id == especialidade_id)

        # Count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Results
        stmt = stmt.offset(skip).limit(limit).order_by(Medico.created_at.desc())
        result = await self.db.execute(stmt)
        medicos = list(result.scalars().all())

        return medicos, total

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Medico]:
        result = await self.db.execute(
            select(Medico)
            .where(Medico.is_ativo == True)
            .options(selectinload(Medico.especialidade))
            .offset(skip)
            .limit(limit)
            .order_by(Medico.created_at.desc())
        )
        return list(result.scalars().all())

    # Agenda
    async def add_agenda(self, medico_id: int, agenda: AgendaMedico) -> AgendaMedico:
        medico = await self.get_by_id(medico_id)
        if not medico:
            raise NotFoundException("Médico não encontrado")

        self.db.add(agenda)
        await self.db.flush()
        await self.db.refresh(agenda)
        return agenda

    async def remove_agenda(self, agenda_id: int) -> None:
        result = await self.db.execute(select(AgendaMedico).where(AgendaMedico.id == agenda_id))
        agenda = result.scalar_one_or_none()
        if not agenda:
            raise NotFoundException("Agenda não encontrada")
        await self.db.delete(agenda)


class EspecialidadeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, especialidade_id: int) -> Especialidade | None:
        result = await self.db.execute(
            select(Especialidade).where(Especialidade.id == especialidade_id)
        )
        return result.scalar_one_or_none()

    async def get_by_nome(self, nome: str) -> Especialidade | None:
        result = await self.db.execute(
            select(Especialidade).where(Especialidade.nome == nome)
        )
        return result.scalar_one_or_none()

    async def create(self, especialidade: Especialidade) -> Especialidade:
        existing = await self.get_by_nome(especialidade.nome)
        if existing:
            raise ConflictException("Especialidade já existe")

        self.db.add(especialidade)
        await self.db.flush()
        await self.db.refresh(especialidade)
        return especialidade

    async def list_all(self) -> list[Especialidade]:
        result = await self.db.execute(
            select(Especialidade).order_by(Especialidade.nome)
        )
        return list(result.scalars().all())
