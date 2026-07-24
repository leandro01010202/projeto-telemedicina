from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domains.prontuario.models import Prontuario, Anotacao, Evolucao, Exame
from core.exceptions import NotFoundException


class ProntuarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_paciente_id(self, paciente_id: int) -> Prontuario | None:
        result = await self.db.execute(
            select(Prontuario)
            .where(Prontuario.paciente_id == paciente_id)
            .options(
                selectinload(Prontuario.anotacoes),
                selectinload(Prontuario.evolucoes),
                selectinload(Prontuario.exames),
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, paciente_id: int) -> Prontuario:
        prontuario = await self.get_by_paciente_id(paciente_id)
        if not prontuario:
            prontuario = Prontuario(paciente_id=paciente_id)
            self.db.add(prontuario)
            await self.db.flush()
            await self.db.refresh(prontuario)
        return prontuario

    # Anotações
    async def add_anotacao(self, prontuario_id: int, anotacao: Anotacao) -> Anotacao:
        prontuario = await self.get_by_paciente_id(prontuario_id)
        if not prontuario:
            raise NotFoundException("Prontuário não encontrado")

        self.db.add(anotacao)
        await self.db.flush()
        await self.db.refresh(anotacao)
        return anotacao

    async def delete_anotacao(self, anotacao_id: int) -> None:
        result = await self.db.execute(select(Anotacao).where(Anotacao.id == anotacao_id))
        anotacao = result.scalar_one_or_none()
        if not anotacao:
            raise NotFoundException("Anotação não encontrada")
        await self.db.delete(anotacao)

    # Evoluções
    async def add_evolucao(self, prontuario_id: int, evolucao: Evolucao) -> Evolucao:
        prontuario = await self.get_by_paciente_id(prontuario_id)
        if not prontuario:
            raise NotFoundException("Prontuário não encontrado")

        self.db.add(evolucao)
        await self.db.flush()
        await self.db.refresh(evolucao)
        return evolucao

    # Exames
    async def add_exame(self, prontuario_id: int, exame: Exame) -> Exame:
        prontuario = await self.get_by_paciente_id(prontuario_id)
        if not prontuario:
            raise NotFoundException("Prontuário não encontrado")

        self.db.add(exame)
        await self.db.flush()
        await self.db.refresh(exame)
        return exame

    async def update_exame(self, exame_id: int, data: dict) -> Exame:
        result = await self.db.execute(select(Exame).where(Exame.id == exame_id))
        exame = result.scalar_one_or_none()
        if not exame:
            raise NotFoundException("Exame não encontrado")

        for field, value in data.items():
            setattr(exame, field, value)

        await self.db.flush()
        await self.db.refresh(exame)
        return exame
