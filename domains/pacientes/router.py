from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from domains.pacientes.schemas import (
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse,
    PacienteSearchResponse,
    AlergiaCreate,
    AlergiaResponse,
    ComorbidadeCreate,
    ComorbidadeResponse,
)
from domains.pacientes.service import PacienteService


def get_current_user():
    from core.dependencies import get_current_user as gcu
    return gcu


router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.get("", response_model=PacienteSearchResponse)
async def listar_pacientes(
    q: str | None = Query(None, description="Buscar por CPF"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = PacienteService(db)
    return await service.search(query=q, skip=skip, limit=limit)


@router.post("", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
async def criar_paciente(
    data: PacienteCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = PacienteService(db)
    return await service.create(data, current_user)


@router.get("/me", response_model=PacienteResponse)
async def meu_paciente(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = PacienteService(db)
    return await service.get_by_user_id(current_user.id)


@router.get("/{paciente_id}", response_model=PacienteResponse)
async def obter_paciente(
    paciente_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = PacienteService(db)
    return await service.get_by_id(paciente_id)


@router.patch("/{paciente_id}", response_model=PacienteResponse)
async def atualizar_paciente(
    paciente_id: int,
    data: PacienteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = PacienteService(db)
    return await service.update(paciente_id, data)


@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_paciente(
    paciente_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = PacienteService(db)
    await service.delete(paciente_id)


# Alergias
@router.post("/{paciente_id}/alergias", response_model=AlergiaResponse, status_code=status.HTTP_201_CREATED)
async def adicionar_alergia(
    paciente_id: int,
    data: AlergiaCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = PacienteService(db)
    return await service.add_alergia(paciente_id, data)


@router.delete("/{paciente_id}/alergias/{alergia_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_alergia(
    paciente_id: int,
    alergia_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = PacienteService(db)
    await service.remove_alergia(paciente_id, alergia_id)


# Comorbidades
@router.post("/{paciente_id}/comorbidades", response_model=ComorbidadeResponse, status_code=status.HTTP_201_CREATED)
async def adicionar_comorbidade(
    paciente_id: int,
    data: ComorbidadeCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = PacienteService(db)
    return await service.add_comorbidade(paciente_id, data)


@router.delete("/{paciente_id}/comorbidades/{comorbidade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_comorbidade(
    paciente_id: int,
    comorbidade_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = PacienteService(db)
    await service.remove_comorbidade(paciente_id, comorbidade_id)
