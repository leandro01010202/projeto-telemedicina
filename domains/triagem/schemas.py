from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TriagemCreate(BaseModel):
    consulta_id: int
    paciente_id: int
    pressao_sistolica: int | None = Field(None, ge=60, le=300)
    pressao_distolica: int | None = Field(None, ge=40, le=200)
    frequencia_cardiaca: int | None = Field(None, ge=30, le=250)
    temperatura: float | None = Field(None, ge=30.0, le=45.0)
    saturacao_oxigenio: int | None = Field(None, ge=50, le=100)
    frequencia_respiratoria: int | None = Field(None, ge=5, le=60)
    peso: float | None = Field(None, ge=0.5, le=500)
    altura: float | None = Field(None, ge=0.3, le=3.0)
    escala_dor: int | None = Field(None, ge=0, le=10)
    queixas: str | None = None


class TriagemResponse(TriagemCreate):
    id: int
    paciente_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
