from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ItemReceitaBase(BaseModel):
    medicamento: str = Field(..., min_length=1, max_length=255)
    concentracao: str | None = None
    quantidade: int = Field(..., ge=1)
    posologia: str = Field(..., min_length=1)
    via_administracao: str | None = None


class ItemReceitaCreate(ItemReceitaBase):
    pass


class ItemReceitaResponse(ItemReceitaBase):
    id: int
    receita_id: int

    model_config = ConfigDict(from_attributes=True)


class ReceitaBase(BaseModel):
    paciente_id: int
    validade_dias: int = Field(default=30, ge=1, le=365)
    observacoes: str | None = None


class ReceitaCreate(ReceitaBase):
    consulta_id: int | None = None
    itens: list[ItemReceitaCreate]


class ReceitaResponse(ReceitaBase):
    id: int
    medico_id: int
    consulta_id: int | None
    esta_assinada: bool
    created_at: datetime
    itens: list[ItemReceitaResponse]

    model_config = ConfigDict(from_attributes=True)


class AtestadoBase(BaseModel):
    paciente_id: int
    cid: str | None = None
    dias: int = Field(..., ge=1, le=365)
    motivo: str = Field(..., min_length=1)


class AtestadoCreate(AtestadoBase):
    consulta_id: int | None = None


class AtestadoResponse(AtestadoBase):
    id: int
    medico_id: int
    consulta_id: int | None
    esta_assinado: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssinaturaRequest(BaseModel):
    pin: str = Field(..., min_length=4, max_length=6)
