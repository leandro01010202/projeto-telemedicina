from domains.consultas.models import Consulta, StatusHistorico, StatusConsulta
from domains.consultas.schemas import (
    ConsultaCreate,
    ConsultaUpdate,
    ConsultaResponse,
    ConsultaSearchResponse,
    ConsultaStatusUpdate,
)
from domains.consultas.repository import ConsultaRepository
from domains.consultas.service import ConsultaService
from domains.consultas.router import router as consultas_router

__all__ = [
    "Consulta",
    "StatusHistorico",
    "StatusConsulta",
    "ConsultaCreate",
    "ConsultaUpdate",
    "ConsultaResponse",
    "ConsultaSearchResponse",
    "ConsultaStatusUpdate",
    "ConsultaRepository",
    "ConsultaService",
    "consultas_router",
]
