from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domains.auditoria.models import LogAuditoria
from domains.auditoria.schemas import LogAuditoriaResponse, AuditoriaSearchResponse


class AuditoriaService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        acao: str,
        usuario_id: int | None = None,
        recurso: str | None = None,
        recurso_id: int | None = None,
        detalhes: str | None = None,
        ip_origem: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        log_entry = LogAuditoria(
            usuario_id=usuario_id,
            acao=acao,
            recurso=recurso,
            recurso_id=recurso_id,
            detalhes=detalhes,
            ip_origem=ip_origem,
            user_agent=user_agent,
        )
        self.db.add(log_entry)
        await self.db.flush()

    async def search(
        self,
        usuario_id: int | None = None,
        acao: str | None = None,
        recurso: str | None = None,
        data_inicio: datetime | None = None,
        data_fim: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> AuditoriaSearchResponse:
        stmt = select(LogAuditoria)

        if usuario_id:
            stmt = stmt.where(LogAuditoria.usuario_id == usuario_id)
        if acao:
            stmt = stmt.where(LogAuditoria.acao == acao)
        if recurso:
            stmt = stmt.where(LogAuditoria.recurso == recurso)
        if data_inicio:
            stmt = stmt.where(LogAuditoria.created_at >= data_inicio)
        if data_fim:
            stmt = stmt.where(LogAuditoria.created_at <= data_fim)

        # Count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Results
        stmt = stmt.offset(skip).limit(limit).order_by(LogAuditoria.created_at.desc())
        result = await self.db.execute(stmt)
        logs = [LogAuditoriaResponse.model_validate(log) for log in result.scalars().all()]

        return AuditoriaSearchResponse(total=total, logs=logs)
