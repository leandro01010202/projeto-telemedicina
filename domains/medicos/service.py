from sqlalchemy.ext.asyncio import AsyncSession

from domains.medicos.models import Medico, Especialidade, AgendaMedico
from domains.medicos.schemas import (
    MedicoCreate,
    MedicoUpdate,
    MedicoResponse,
    MedicoSearchResponse,
    AgendaMedicoCreate,
    AgendaMedicoResponse,
    EspecialidadeCreate,
    EspecialidadeResponse,
)
from domains.medicos.repository import MedicoRepository, EspecialidadeRepository
from core.exceptions import NotFoundException
from domains.auth.models import User


class MedicoService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = MedicoRepository(db)

    async def create(self, data: MedicoCreate, current_user: User | None = None) -> MedicoResponse:
        medico = Medico(
            crm=data.crm,
            crm_estado=data.crm_estado,
            especialidade_id=data.especialidade_id,
            telefone=data.telefone,
            cpf=data.cpf,
            tempo_consulta_minutos=data.tempo_consulta_minutos,
            user_id=data.user_id or (current_user.id if current_user else None),
        )
        created = await self.repository.create(medico)
        return await self.get_by_id(created.id)

    async def get_by_id(self, medico_id: int) -> MedicoResponse:
        medico = await self.repository.get_by_id(medico_id)
        if not medico:
            raise NotFoundException("Médico não encontrado")
        return MedicoResponse.model_validate(medico)

    async def get_by_user_id(self, user_id: int) -> MedicoResponse:
        medico = await self.repository.get_by_user_id(user_id)
        if not medico:
            raise NotFoundException("Médico não encontrado para este usuário")
        return MedicoResponse.model_validate(medico)

    async def update(self, medico_id: int, data: MedicoUpdate) -> MedicoResponse:
        medico = await self.repository.get_by_id(medico_id)
        if not medico:
            raise NotFoundException("Médico não encontrado")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(medico, field, value)

        updated = await self.repository.update(medico)
        return await self.get_by_id(updated.id)

    async def delete(self, medico_id: int) -> None:
        await self.repository.delete(medico_id)

    async def search(
        self,
        query: str | None = None,
        especialidade_id: int | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> MedicoSearchResponse:
        medicos, total = await self.repository.search(query, especialidade_id, skip, limit)
        return MedicoSearchResponse(
            total=total,
            medicos=[MedicoResponse.model_validate(m) for m in medicos],
        )

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[MedicoResponse]:
        medicos = await self.repository.list_all(skip, limit)
        return [MedicoResponse.model_validate(m) for m in medicos]

    async def add_agenda(self, medico_id: int, data: AgendaMedicoCreate) -> AgendaMedicoResponse:
        agenda = AgendaMedico(
            medico_id=medico_id,
            dia_semana=data.dia_semana,
            hora_inicio=data.hora_inicio,
            hora_fim=data.hora_fim,
            ativo=data.ativo,
        )
        created = await self.repository.add_agenda(medico_id, agenda)
        return AgendaMedicoResponse.model_validate(created)

    async def remove_agenda(self, medico_id: int, agenda_id: int) -> None:
        await self.repository.remove_agenda(agenda_id)


class EspecialidadeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = EspecialidadeRepository(db)

    async def create(self, data: EspecialidadeCreate) -> EspecialidadeResponse:
        especialidade = Especialidade(
            nome=data.nome,
            descricao=data.descricao,
        )
        created = await self.repository.create(especialidade)
        return EspecialidadeResponse.model_validate(created)

    async def get_by_id(self, especialidade_id: int) -> EspecialidadeResponse:
        especialidade = await self.repository.get_by_id(especialidade_id)
        if not especialidade:
            raise NotFoundException("Especialidade não encontrada")
        return EspecialidadeResponse.model_validate(especialidade)

    async def list_all(self) -> list[EspecialidadeResponse]:
        especialidades = await self.repository.list_all()
        return [EspecialidadeResponse.model_validate(e) for e in especialidades]
