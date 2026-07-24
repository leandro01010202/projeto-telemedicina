from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from domains.triagem.schemas import TriagemCreate, TriagemResponse
from domains.triagem.service import TriagemService


def get_current_user():
    from core.dependencies import get_current_user as gcu
    return gcu

router = APIRouter(prefix="/triagem", tags=["Triagem"])


@router.post("", response_model=TriagemResponse, status_code=status.HTTP_201_CREATED)
async def criar_triagem(
    data: TriagemCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = TriagemService(db)
    return await service.create(data)


@router.get("/{consulta_id}", response_model=TriagemResponse)
async def obter_triagem(
    consulta_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = TriagemService(db)
    return await service.get_by_consulta(consulta_id)
