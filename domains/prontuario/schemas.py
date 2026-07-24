from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AnotacaoBase(BaseModel):
    conteudo: str = Field(..., min_length=1)


class AnotacaoCreate(AnotacaoBase):
    consulta_id: int | None = None


class AnotacaoResponse(AnotacaoBase):
    id: int
    prontuario_id: int
    consulta_id: int | None
    medico_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvolucaoBase(BaseModel):
    tipo: str = Field(..., pattern="^(inicial|evolucao|alta)$")
    descricao: str = Field(..., min_length=1)


class EvolucaoCreate(EvolucaoBase):
    consulta_id: int | None = None


class EvolucaoResponse(EvolucaoBase):
    id: int
    prontuario_id: int
    consulta_id: int | None
    medico_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExameBase(BaseModel):
    nome: str = Field(..., min_length=1)
    tipo: str | None = None
    resultado: str | None = None


class ExameCreate(ExameBase):
    consulta_id: int | None = None


class ExameUpdate(BaseModel):
    resultado: str | None = None
    arquivo_url: str | None = None


class ExameResponse(ExameBase):
    id: int
    prontuario_id: int
    consulta_id: int | None
    data_solicitacao: datetime
    data_resultado: datetime | None
    arquivo_url: str | None

    model_config = ConfigDict(from_attributes=True)


class ProntuarioResponse(BaseModel):
    id: int
    paciente_id: int
    created_at: datetime
    updated_at: datetime
    anotacoes: list[AnotacaoResponse] = []
    evolucoes: list[EvolucaoResponse] = []
    exames: list[ExameResponse] = []

    model_config = ConfigDict(from_attributes=True)
