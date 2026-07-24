from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from domains.auth.schemas import UserResponse


class EspecialidadeBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: str | None = None


class EspecialidadeCreate(EspecialidadeBase):
    pass


class EspecialidadeResponse(EspecialidadeBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgendaMedicoBase(BaseModel):
    dia_semana: int = Field(..., ge=0, le=6)
    hora_inicio: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    hora_fim: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    ativo: bool = True


class AgendaMedicoCreate(AgendaMedicoBase):
    pass


class AgendaMedicoResponse(AgendaMedicoBase):
    id: int
    medico_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicoBase(BaseModel):
    crm: str = Field(..., min_length=4, max_length=20)
    crm_estado: str = Field(..., min_length=2, max_length=2)
    especialidade_id: int | None = None
    telefone: str | None = None
    cpf: str = Field(..., min_length=11, max_length=14)
    tempo_consulta_minutos: int = Field(default=30, ge=10, le=120)


class MedicoCreate(MedicoBase):
    user_id: int | None = None


class MedicoUpdate(BaseModel):
    especialidade_id: int | None = None
    telefone: str | None = None
    tempo_consulta_minutos: int | None = Field(None, ge=10, le=120)


class MedicoResponse(MedicoBase):
    id: int
    user_id: int | None
    is_ativo: bool
    created_at: datetime
    updated_at: datetime
    especialidade: EspecialidadeResponse | None = None
    agenda: list[AgendaMedicoResponse] = []

    model_config = ConfigDict(from_attributes=True)


class MedicoListResponse(BaseModel):
    id: int
    crm: str
    crm_estado: str
    telefone: str | None
    is_ativo: bool
    especialidade: EspecialidadeResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class MedicoSearchResponse(BaseModel):
    total: int
    medicos: list[MedicoListResponse]
