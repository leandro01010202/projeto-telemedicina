from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LogAuditoriaResponse(BaseModel):
    id: int
    usuario_id: int | None
    acao: str
    recurso: str | None
    recurso_id: int | None
    detalhes: str | None
    ip_origem: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditoriaSearchResponse(BaseModel):
    total: int
    logs: list[LogAuditoriaResponse]
