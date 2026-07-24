from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
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
from domains.medicos.service import MedicoService, EspecialidadeService


def get_current_user():
    from core.dependencies import get_current_user as gcu
    return gcu


router = APIRouter(prefix="/medicos", tags=["Médicos"])
router_esp = APIRouter(prefix="/especialidades", tags=["Especialidades"])


# Médicos
@router.get("", response_model=MedicoSearchResponse)
async def listar_medicos(
    q: str | None = Query(None, description="Buscar por CRM ou CPF"),
    especialidade_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = MedicoService(db)
    return await service.search(query=q, especialidade_id=especialidade_id, skip=skip, limit=limit)


@router.post("", response_model=MedicoResponse, status_code=status.HTTP_201_CREATED)
async def criar_medico(
    data: MedicoCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = MedicoService(db)
    return await service.create(data, current_user)


@router.get("/me", response_model=MedicoResponse)
async def meu_medico(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = MedicoService(db)
    return await service.get_by_user_id(current_user.id)


@router.get("/{medico_id}", response_model=MedicoResponse)
async def obter_medico(
    medico_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = MedicoService(db)
    return await service.get_by_id(medico_id)


@router.patch("/{medico_id}", response_model=MedicoResponse)
async def atualizar_medico(
    medico_id: int,
    data: MedicoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = MedicoService(db)
    return await service.update(medico_id, data)


@router.delete("/{medico_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_medico(
    medico_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = MedicoService(db)
    await service.delete(medico_id)


# Agenda
@router.post("/{medico_id}/agenda", response_model=AgendaMedicoResponse, status_code=status.HTTP_201_CREATED)
async def adicionar_agenda(
    medico_id: int,
    data: AgendaMedicoCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = MedicoService(db)
    return await service.add_agenda(medico_id, data)


@router.delete("/{medico_id}/agenda/{agenda_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_agenda(
    medico_id: int,
    agenda_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = MedicoService(db)
    await service.remove_agenda(medico_id, agenda_id)


# Especialidades
@router_esp.get("", response_model=list[EspecialidadeResponse])
async def listar_especialidades(
    db: AsyncSession = Depends(get_db),
):
    service = EspecialidadeService(db)
    return await service.list_all()


@router_esp.post("", response_model=EspecialidadeResponse, status_code=status.HTTP_201_CREATED)
async def criar_especialidade(
    data: EspecialidadeCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = EspecialidadeService(db)
    return await service.create(data)


@router_esp.get("/{especialidade_id}", response_model=EspecialidadeResponse)
async def obter_especialidade(
    especialidade_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = EspecialidadeService(db)
    return await service.get_by_id(especialidade_id)
