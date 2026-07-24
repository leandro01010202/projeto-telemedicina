from datetime import datetime, date
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domains.consultas.models import Consulta, StatusHistorico, StatusConsulta
from core.exceptions import NotFoundException, ConflictException, ValidationException


class ConsultaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, consulta_id: int) -> Consulta | None:
        result = await self.db.execute(
            select(Consulta)
            .where(Consulta.id == consulta_id)
            .options(selectinload(Consulta.historico))
        )
        return result.scalar_one_or_none()

    async def get_by_sala(self, sala_webrtc: str) -> Consulta | None:
        result = await self.db.execute(
            select(Consulta).where(Consulta.sala_webrtc == sala_webrtc)
        )
        return result.scalar_one_or_none()

    async def create(self, consulta: Consulta) -> Consulta:
        # Verificar conflito de horário
        conflito = await self._check_conflito(
            consulta.medico_id,
            consulta.data_hora,
            consulta.duracao_minutos,
        )
        if conflito:
            raise ConflictException("Horário conflito com outra consulta")

        self.db.add(consulta)
        await self.db.flush()
        await self.db.refresh(consulta)

        # Registrar histórico
        await self._add_historico(consulta.id, None, StatusConsulta.AGENDADA.value)
        return consulta

    async def update(self, consulta: Consulta) -> Consulta:
        await self.db.flush()
        await self.db.refresh(consulta)
        return consulta

    async def delete(self, consulta_id: int) -> None:
        consulta = await self.get_by_id(consulta_id)
        if not consulta:
            raise NotFoundException("Consulta não encontrada")
        await self.db.delete(consulta)

    async def update_status(
        self,
        consulta_id: int,
        novo_status: StatusConsulta,
        observacao: str | None = None,
        user_id: int | None = None,
    ) -> Consulta:
        consulta = await self.get_by_id(consulta_id)
        if not consulta:
            raise NotFoundException("Consulta não encontrada")

        status_anterior = consulta.status.value
        consulta.status = novo_status

        # Atualizar timestamps específicos
        if novo_status == StatusConsulta.EM_ANDAMENTO:
            consulta.data_inicio = datetime.now()
        elif novo_status == StatusConsulta.FINALIZADA:
            consulta.data_fim = datetime.now()

        await self._add_historico(
            consulta.id, status_anterior, novo_status.value, observacao, user_id
        )
        await self.db.flush()
        await self.db.refresh(consulta)
        return consulta

    async def _add_historico(
        self,
        consulta_id: int,
        status_anterior: str | None,
        status_novo: str,
        observacao: str | None = None,
        alterado_por: int | None = None,
    ) -> None:
        historico = StatusHistorico(
            consulta_id=consulta_id,
            status_anterior=status_anterior,
            status_novo=status_novo,
            observacao=observacao,
            alterado_por=alterado_por,
        )
        self.db.add(historico)
        await self.db.flush()

    async def _check_conflito(
        self,
        medico_id: int,
        data_hora: datetime,
        duracao_minutos: int,
        exclude_id: int | None = None,
    ) -> bool:
        from datetime import timedelta

        data_fim = data_hora + timedelta(minutes=duracao_minutos)

        stmt = select(Consulta).where(
            and_(
                Consulta.medico_id == medico_id,
                Consulta.status.in_([StatusConsulta.AGENDADA, StatusConsulta.EM_ANDAMENTO]),
                or_(
                    and_(
                        Consulta.data_hora <= data_hora,
                        func.timezone('UTC', Consulta.data_hora) + 
                        timedelta(minutes=Consulta.duracao_minutos) > data_hora
                    ),
                    and_(
                        Consulta.data_hora < data_fim,
                        Consulta.data_hora >= data_hora - timedelta(minutes=Consulta.duracao_minutos)
                    ),
                ),
            )
        )

        if exclude_id:
            stmt = stmt.where(Consulta.id != exclude_id)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def search(
        self,
        paciente_id: int | None = None,
        medico_id: int | None = None,
        status: StatusConsulta | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Consulta], int]:
        stmt = select(Consulta).options(selectinload(Consulta.historico))

        if paciente_id:
            stmt = stmt.where(Consulta.paciente_id == paciente_id)
        if medico_id:
            stmt = stmt.where(Consulta.medico_id == medico_id)
        if status:
            stmt = stmt.where(Consulta.status == status)
        if data_inicio:
            stmt = stmt.where(Consulta.data_hora >= datetime.combine(data_inicio, datetime.min.time()))
        if data_fim:
            stmt = stmt.where(Consulta.data_hora <= datetime.combine(data_fim, datetime.max.time()))

        # Count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Results
        stmt = stmt.offset(skip).limit(limit).order_by(Consulta.data_hora.desc())
        result = await self.db.execute(stmt)
        consultas = list(result.scalars().all())

        return consultas, total

    async def list_hoje(self, usuario_id: int | None = None, tipo: str | None = None) -> list[Consulta]:
        hoje = datetime.now().date()
        data_inicio = datetime.combine(hoje, datetime.min.time())
        data_fim = datetime.combine(hoje, datetime.max.time())

        stmt = select(Consulta).where(
            and_(
                Consulta.data_hora >= data_inicio,
                Consulta.data_hora <= data_fim,
            )
        )

        if tipo == "medico" and usuario_id:
            # Assumindo que usuario_id corresponde a user_id do médico
            from domains.medicos.models import Medico
            medico_result = await self.db.execute(
                select(Medico.id).where(Medico.user_id == usuario_id)
            )
            medico_ids = [m[0] for m in medico_result.all()]
            if medico_ids:
                stmt = stmt.where(Consulta.medico_id.in_(medico_ids))

        stmt = stmt.order_by(Consulta.data_hora)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_status(self) -> dict[str, int]:
        result = await self.db.execute(
            select(Consulta.status, func.count(Consulta.id))
            .group_by(Consulta.status)
        )
        return {status.value: count for status, count in result.all()}
