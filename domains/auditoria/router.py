from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from domains.auditoria.schemas import AuditoriaSearchResponse
from domains.auditoria.service import AuditoriaService


def get_current_user():
    from core.dependencies import get_current_user as gcu
    return gcu

router = APIRouter(prefix="/auditoria", tags=["Auditoria"])


@router.get("", response_model=AuditoriaSearchResponse)
async def listar_logs(
    usuario_id: int | None = Query(None),
    acao: str | None = Query(None),
    recurso: str | None = Query(None),
    data_inicio: datetime | None = Query(None),
    data_fim: datetime | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = AuditoriaService(db)
    return await service.search(
        usuario_id=usuario_id,
        acao=acao,
        recurso=recurso,
        data_inicio=data_inicio,
        data_fim=data_fim,
        skip=skip,
        limit=limit,
    )
