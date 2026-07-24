from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from domains.prontuario.schemas import (
    AnotacaoCreate,
    AnotacaoResponse,
    EvolucaoCreate,
    EvolucaoResponse,
    ExameCreate,
    ExameUpdate,
    ExameResponse,
    ProntuarioResponse,
)
from domains.prontuario.service import ProntuarioService


def get_current_user():
    from core.dependencies import get_current_user as gcu
    return gcu

router = APIRouter(prefix="/prontuario", tags=["Prontuário"])


@router.get("/{paciente_id}", response_model=ProntuarioResponse)
async def obter_prontuario(
    paciente_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ProntuarioService(db)
    return await service.get_by_paciente(paciente_id)


@router.post("/{paciente_id}/anotacoes", response_model=AnotacaoResponse, status_code=status.HTTP_201_CREATED)
async def criar_anotacao(
    paciente_id: int,
    data: AnotacaoCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ProntuarioService(db)
    return await service.add_anotacao(paciente_id, data, current_user)


@router.delete("/{paciente_id}/anotacoes/{anotacao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_anotacao(
    paciente_id: int,
    anotacao_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ProntuarioService(db)
    await service.delete_anotacao(paciente_id, anotacao_id)


@router.post("/{paciente_id}/evolucoes", response_model=EvolucaoResponse, status_code=status.HTTP_201_CREATED)
async def criar_evolucao(
    paciente_id: int,
    data: EvolucaoCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ProntuarioService(db)
    return await service.add_evolucao(paciente_id, data, current_user)


@router.post("/{paciente_id}/exames", response_model=ExameResponse, status_code=status.HTTP_201_CREATED)
async def criar_exame(
    paciente_id: int,
    data: ExameCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ProntuarioService(db)
    return await service.add_exame(paciente_id, data)


@router.patch("/{paciente_id}/exames/{exame_id}", response_model=ExameResponse)
async def atualizar_exame(
    paciente_id: int,
    exame_id: int,
    data: ExameUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = ProntuarioService(db)
    return await service.update_exame(paciente_id, exame_id, data)
