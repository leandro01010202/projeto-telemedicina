from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from domains.dashboard.service import DashboardService, DashboardStats, ConsultasPorDia


def get_current_user():
    from core.dependencies import get_current_user as gcu
    return gcu

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/resumo", response_model=DashboardStats)
async def obter_resumo(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = DashboardService(db)
    return await service.get_stats()


@router.get("/consultas-por-dia", response_model=list[ConsultasPorDia])
async def obter_consultas_por_dia(
    dias: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user()),
):
    service = DashboardService(db)
    return await service.get_consultas_por_dia(dias)
