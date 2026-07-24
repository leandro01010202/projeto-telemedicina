from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from domains.prontuario.models import Prontuario, Anotacao, Evolucao, Exame
from domains.prontuario.schemas import (
    AnotacaoCreate,
    AnotacaoResponse,
    EvolucaoCreate,
    EvolucaoResponse,
    ExameCreate,
    ExameUpdate,
    ExameResponse,
    ProntuarioResponse,
)
from domains.prontuario.repository import ProntuarioRepository
from domains.auth.models import User


class ProntuarioService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ProntuarioRepository(db)

    async def get_by_paciente(self, paciente_id: int) -> ProntuarioResponse:
        prontuario = await self.repository.get_or_create(paciente_id)
        return ProntuarioResponse.model_validate(prontuario)

    async def add_anotacao(
        self,
        paciente_id: int,
        data: AnotacaoCreate,
        current_user: User,
    ) -> AnotacaoResponse:
        prontuario = await self.repository.get_or_create(paciente_id)
        
        # Obter medico_id se o usuário for médico
        medico_id = None
        from domains.medicos.models import Medico
        from sqlalchemy import select
        result = await self.db.execute(
            select(Medico.id).where(Medico.user_id == current_user.id)
        )
        medico_row = result.first()
        if medico_row:
            medico_id = medico_row[0]

        anotacao = Anotacao(
            prontuario_id=prontuario.id,
            consulta_id=data.consulta_id,
            medico_id=medico_id,
            conteudo=data.conteudo,
        )
        created = await self.repository.add_anotacao(prontuario.id, anotacao)
        return AnotacaoResponse.model_validate(created)

    async def delete_anotacao(self, paciente_id: int, anotacao_id: int) -> None:
        await self.repository.delete_anotacao(anotacao_id)

    async def add_evolucao(
        self,
        paciente_id: int,
        data: EvolucaoCreate,
        current_user: User,
    ) -> EvolucaoResponse:
        prontuario = await self.repository.get_or_create(paciente_id)

        medico_id = None
        from domains.medicos.models import Medico
        from sqlalchemy import select
        result = await self.db.execute(
            select(Medico.id).where(Medico.user_id == current_user.id)
        )
        medico_row = result.first()
        if medico_row:
            medico_id = medico_row[0]

        evolucao = Evolucao(
            prontuario_id=prontuario.id,
            consulta_id=data.consulta_id,
            medico_id=medico_id,
            tipo=data.tipo,
            descricao=data.descricao,
        )
        created = await self.repository.add_evolucao(prontuario.id, evolucao)
        return EvolucaoResponse.model_validate(created)

    async def add_exame(
        self,
        paciente_id: int,
        data: ExameCreate,
    ) -> ExameResponse:
        prontuario = await self.repository.get_or_create(paciente_id)

        exame = Exame(
            prontuario_id=prontuario.id,
            consulta_id=data.consulta_id,
            nome=data.nome,
            tipo=data.tipo,
            resultado=data.resultado,
        )
        created = await self.repository.add_exame(prontuario.id, exame)
        return ExameResponse.model_validate(created)

    async def update_exame(
        self,
        paciente_id: int,
        exame_id: int,
        data: ExameUpdate,
    ) -> ExameResponse:
        update_data = data.model_dump(exclude_unset=True)
        if update_data.get("resultado") and not update_data.get("data_resultado"):
            update_data["data_resultado"] = datetime.now()
        
        updated = await self.repository.update_exame(exame_id, update_data)
        return ExameResponse.model_validate(updated)
