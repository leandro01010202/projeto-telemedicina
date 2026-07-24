from sqlalchemy.ext.asyncio import AsyncSession

from domains.triagem.models import Triagem
from domains.triagem.schemas import TriagemCreate, TriagemResponse
from core.exceptions import ConflictException, NotFoundException


class TriagemService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: TriagemCreate) -> TriagemResponse:
        from sqlalchemy import select
        
        # Verificar se já existe triagem para esta consulta
        result = await self.db.execute(
            select(Triagem).where(Triagem.consulta_id == data.consulta_id)
        )
        if result.scalar_one_or_none():
            raise ConflictException("Triagem já existe para esta consulta")

        triagem = Triagem(
            consulta_id=data.consulta_id,
            paciente_id=data.paciente_id,
            pressao_sistolica=data.pressao_sistolica,
            pressao_distolica=data.pressao_distolica,
            frequencia_cardiaca=data.frequencia_cardiaca,
            temperatura=data.temperatura,
            saturacao_oxigenio=data.saturacao_oxigenio,
            frequencia_respiratoria=data.frequencia_respiratoria,
            peso=data.peso,
            altura=data.altura,
            escala_dor=data.escala_dor,
            queixas=data.queixas,
        )
        self.db.add(triagem)
        await self.db.flush()
        await self.db.refresh(triagem)
        return TriagemResponse.model_validate(triagem)

    async def get_by_consulta(self, consulta_id: int) -> TriagemResponse:
        from sqlalchemy import select
        
        result = await self.db.execute(
            select(Triagem).where(Triagem.consulta_id == consulta_id)
        )
        triagem = result.scalar_one_or_none()
        if not triagem:
            raise NotFoundException("Triagem não encontrada")
        return TriagemResponse.model_validate(triagem)
