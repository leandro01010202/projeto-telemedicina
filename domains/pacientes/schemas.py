from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict

from domains.auth.schemas import UserResponse


class PacienteBase(BaseModel):
    cpf: str = Field(..., min_length=11, max_length=14)
    data_nascimento: date
    telefone: str | None = None
    sexo: str | None = Field(None, pattern="^[MFO]$")
    endereco: str | None = None
    cidade: str | None = None
    estado: str | None = Field(None, max_length=2)
    cep: str | None = None
    observacoes: str | None = None


class PacienteCreate(PacienteBase):
    user_id: int | None = None


class PacienteUpdate(BaseModel):
    telefone: str | None = None
    sexo: str | None = Field(None, pattern="^[MFO]$")
    endereco: str | None = None
    cidade: str | None = None
    estado: str | None = Field(None, max_length=2)
    cep: str | None = None
    observacoes: str | None = None


class AlergiaBase(BaseModel):
    sustancia: str = Field(..., min_length=1, max_length=255)
    tipo_reacao: str | None = None
    gravidade: str = Field(default="leve", pattern="^(leve|moderada|grave)$")


class AlergiaCreate(AlergiaBase):
    pass


class AlergiaResponse(AlergiaBase):
    id: int
    paciente_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComorbidadeBase(BaseModel):
    condicao: str = Field(..., min_length=1, max_length=255)
    diagnostico_data: date | None = None
    em_tratamento: bool = True
    observacoes: str | None = None


class ComorbidadeCreate(ComorbidadeBase):
    pass


class ComorbidadeResponse(ComorbidadeBase):
    id: int
    paciente_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PacienteResponse(PacienteBase):
    id: int
    user_id: int | None
    created_at: datetime
    updated_at: datetime
    alergias: list[AlergiaResponse] = []
    comorbidades: list[ComorbidadeResponse] = []

    model_config = ConfigDict(from_attributes=True)


class PacienteListResponse(BaseModel):
    id: int
    cpf: str
    data_nascimento: date
    telefone: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PacienteSearchResponse(BaseModel):
    total: int
    pacientes: list[PacienteListResponse]
