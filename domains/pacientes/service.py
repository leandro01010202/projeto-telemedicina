from sqlalchemy.ext.asyncio import AsyncSession

from domains.pacientes.models import Paciente, Alergia, Comorbidade
from domains.pacientes.schemas import (
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse,
    AlergiaCreate,
    AlergiaResponse,
    ComorbidadeCreate,
    ComorbidadeResponse,
    PacienteSearchResponse,
)
from domains.pacientes.repository import PacienteRepository
from core.exceptions import NotFoundException, ForbiddenException
from core.dependencies import get_current_user
from domains.auth.models import User


class PacienteService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = PacienteRepository(db)

    async def create(self, data: PacienteCreate, current_user: User | None = None) -> PacienteResponse:
        paciente = Paciente(
            cpf=data.cpf,
            data_nascimento=data.data_nascimento,
            telefone=data.telefone,
            sexo=data.sexo,
            endereco=data.endereco,
            cidade=data.cidade,
            estado=data.estado,
            cep=data.cep,
            observacoes=data.observacoes,
            user_id=data.user_id or (current_user.id if current_user else None),
        )
        created = await self.repository.create(paciente)
        return await self.get_by_id(created.id)

    async def get_by_id(self, paciente_id: int) -> PacienteResponse:
        paciente = await self.repository.get_by_id(paciente_id)
        if not paciente:
            raise NotFoundException("Paciente não encontrado")
        return PacienteResponse.model_validate(paciente)

    async def get_by_user_id(self, user_id: int) -> PacienteResponse:
        paciente = await self.repository.get_by_user_id(user_id)
        if not paciente:
            raise NotFoundException("Paciente não encontrado para este usuário")
        return PacienteResponse.model_validate(paciente)

    async def update(self, paciente_id: int, data: PacienteUpdate) -> PacienteResponse:
        paciente = await self.repository.get_by_id(paciente_id)
        if not paciente:
            raise NotFoundException("Paciente não encontrado")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(paciente, field, value)

        updated = await self.repository.update(paciente)
        return PacienteResponse.model_validate(updated)

    async def delete(self, paciente_id: int) -> None:
        await self.repository.delete(paciente_id)

    async def search(self, query: str | None = None, skip: int = 0, limit: int = 50) -> PacienteSearchResponse:
        pacientes, total = await self.repository.search(query, skip, limit)
        return PacienteSearchResponse(
            total=total,
            pacientes=[PacienteResponse.model_validate(p) for p in pacientes],
        )

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[PacienteResponse]:
        pacientes = await self.repository.list_all(skip, limit)
        return [PacienteResponse.model_validate(p) for p in pacientes]

    # Alergias
    async def add_alergia(self, paciente_id: int, data: AlergiaCreate) -> AlergiaResponse:
        alergia = Alergia(
            paciente_id=paciente_id,
            sustancia=data.sustancia,
            tipo_reacao=data.tipo_reacao,
            gravidade=data.gravidade,
        )
        created = await self.repository.add_alergia(paciente_id, alergia)
        return AlergiaResponse.model_validate(created)

    async def remove_alergia(self, paciente_id: int, alergia_id: int) -> None:
        await self.repository.remove_alergia(alergia_id)

    # Comorbidades
    async def add_comorbidade(self, paciente_id: int, data: ComorbidadeCreate) -> ComorbidadeResponse:
        comorbidade = Comorbidade(
            paciente_id=paciente_id,
            condicao=data.condicao,
            diagnostico_data=data.diagnostico_data,
            em_tratamento=data.em_tratamento,
            observacoes=data.observacoes,
        )
        created = await self.repository.add_comorbidade(paciente_id, comorbidade)
        return ComorbidadeResponse.model_validate(created)

    async def remove_comorbidade(self, paciente_id: int, comorbidade_id: int) -> None:
        await self.repository.remove_comorbidade(comorbidade_id)
