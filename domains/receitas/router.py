from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from domains.receitas.schemas import (
    ReceitaCreate,
    ReceitaResponse,
    AtestadoCreate,
    AtestadoResponse,
    AssinaturaRequest,
)
from domains.receitas.service import ReceitaService, AtestadoService


def get_current_user():
    from core.dependencies import get_current_user as gcu
    return gcu

router = APIRouter(prefix="/receitas", tags=["Receitas"])
router_atest = APIRouter(prefix="/atestados", tags=["Atestados"])


# Receitas
@router.post("", response_model=ReceitaResponse, status_code=status.HTTP_201_CREATED)
async def criar_receita(
    data: ReceitaCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ReceitaService(db)
    return await service.create(data, current_user)


@router.get("/{receita_id}", response_model=ReceitaResponse)
async def obter_receita(
    receita_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ReceitaService(db)
    return await service.get_by_id(receita_id)


@router.get("/paciente/{paciente_id}", response_model=list[ReceitaResponse])
async def listar_receitas_paciente(
    paciente_id: int,
    include_expired: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ReceitaService(db)
    return await service.list_by_paciente(paciente_id, include_expired)


@router.post("/{receita_id}/assinar", response_model=ReceitaResponse)
async def assinar_receita(
    receita_id: int,
    data: AssinaturaRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ReceitaService(db)
    return await service.sign(receita_id, current_user)


# Atestados
@router_atest.post("", response_model=AtestadoResponse, status_code=status.HTTP_201_CREATED)
async def criar_atestado(
    data: AtestadoCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = AtestadoService(db)
    return await service.create(data, current_user)


@router_atest.get("/{atestado_id}", response_model=AtestadoResponse)
async def obter_atestado(
    atestado_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = AtestadoService(db)
    return await service.get_by_id(atestado_id)


@router_atest.get("/paciente/{paciente_id}", response_model=list[AtestadoResponse])
async def listar_atestados_paciente(
    paciente_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = AtestadoService(db)
    return await service.list_by_paciente(paciente_id)


@router_atest.post("/{atestado_id}/assinar", response_model=AtestadoResponse)
async def assinar_atestado(
    atestado_id: int,
    data: AssinaturaRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = AtestadoService(db)
    return await service.sign(atestado_id, current_user)
