from datetime import date
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from domains.consultas.models import StatusConsulta
from domains.consultas.schemas import (
    ConsultaCreate,
    ConsultaUpdate,
    ConsultaResponse,
    ConsultaSearchResponse,
    ConsultaStatusUpdate,
)
from domains.consultas.service import ConsultaService


def get_current_user():
    from core.dependencies import get_current_user as gcu
    return gcu


router = APIRouter(prefix="/consultas", tags=["Consultas"])


@router.get("", response_model=ConsultaSearchResponse)
async def listar_consultas(
    paciente_id: int | None = Query(None),
    medico_id: int | None = Query(None),
    status: StatusConsulta | None = Query(None),
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ConsultaService(db)
    return await service.search(
        paciente_id=paciente_id,
        medico_id=medico_id,
        status=status,
        data_inicio=data_inicio,
        data_fim=data_fim,
        skip=skip,
        limit=limit,
    )


@router.get("/hoje", response_model=list[ConsultaResponse])
async def consultas_hoje(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ConsultaService(db)
    return await service.list_hoje(current_user)


@router.post("", response_model=ConsultaResponse, status_code=status.HTTP_201_CREATED)
async def criar_consulta(
    data: ConsultaCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ConsultaService(db)
    return await service.create(data, current_user)


@router.get("/{consulta_id}", response_model=ConsultaResponse)
async def obter_consulta(
    consulta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ConsultaService(db)
    return await service.get_by_id(consulta_id)


@router.patch("/{consulta_id}", response_model=ConsultaResponse)
async def atualizar_consulta(
    consulta_id: int,
    data: ConsultaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ConsultaService(db)
    return await service.update(consulta_id, data, current_user)


@router.delete("/{consulta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_consulta(
    consulta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ConsultaService(db)
    await service.delete(consulta_id)


@router.post("/{consulta_id}/iniciar", response_model=ConsultaResponse)
async def iniciar_consulta(
    consulta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ConsultaService(db)
    return await service.iniciar(consulta_id, current_user)


@router.post("/{consulta_id}/finalizar", response_model=ConsultaResponse)
async def finalizar_consulta(
    consulta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ConsultaService(db)
    return await service.finalizar(consulta_id, current_user)


@router.post("/{consulta_id}/cancelar", response_model=ConsultaResponse)
async def cancelar_consulta(
    consulta_id: int,
    data: ConsultaStatusUpdate | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ConsultaService(db)
    observacao = data.observacao if data else None
    return await service.cancelar(consulta_id, current_user, observacao)
