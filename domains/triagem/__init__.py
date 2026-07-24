from domains.triagem.models import Triagem
from domains.triagem.schemas import TriagemCreate, TriagemResponse
from domains.triagem.service import TriagemService
from domains.triagem.router import router as triagem_router

__all__ = [
    "Triagem",
    "TriagemCreate",
    "TriagemResponse",
    "TriagemService",
    "triagem_router",
]
