from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from domains.consultas.models import StatusConsulta


class ConsultaBase(BaseModel):
    paciente_id: int
    medico_id: int
    data_hora: datetime
    duracao_minutos: int = Field(default=30, ge=10, le=180)
    motivo: str | None = None


class ConsultaCreate(ConsultaBase):
    pass


class ConsultaUpdate(BaseModel):
    data_hora: datetime | None = None
    duracao_minutos: int | None = Field(None, ge=10, le=180)
    motivo: str | None = None


class StatusHistoricoResponse(BaseModel):
    id: int
    status_anterior: str | None
    status_novo: str
    observacao: str | None
    alterado_por: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConsultaResponse(ConsultaBase):
    id: int
    status: StatusConsulta
    sala_webrtc: str | None
    data_inicio: datetime | None
    data_fim: datetime | None
    created_at: datetime
    updated_at: datetime
    historico: list[StatusHistoricoResponse] = []

    model_config = ConfigDict(from_attributes=True)


class ConsultaListResponse(BaseModel):
    id: int
    paciente_id: int
    medico_id: int
    data_hora: datetime
    status: StatusConsulta
    motivo: str | None

    model_config = ConfigDict(from_attributes=True)


class ConsultaSearchResponse(BaseModel):
    total: int
    consultas: list[ConsultaListResponse]


class ConsultaStatusUpdate(BaseModel):
    observacao: str | None = None
