import uuid
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from domains.consultas.models import Consulta, StatusConsulta
from domains.consultas.schemas import (
    ConsultaCreate,
    ConsultaUpdate,
    ConsultaResponse,
    ConsultaSearchResponse,
    ConsultaStatusUpdate,
)
from domains.consultas.repository import ConsultaRepository
from events.bus import event_bus
from events.events import ConsultaAgendada
from core.exceptions import NotFoundException, ForbiddenException
from domains.auth.models import User


class ConsultaService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ConsultaRepository(db)

    async def create(self, data: ConsultaCreate, current_user: User | None = None) -> ConsultaResponse:
        consulta = Consulta(
            paciente_id=data.paciente_id,
            medico_id=data.medico_id,
            data_hora=data.data_hora,
            duracao_minutos=data.duracao_minutos,
            motivo=data.motivo,
            sala_webrtc=str(uuid.uuid4()),
        )
        created = await self.repository.create(consulta)

        # Publicar evento
        await event_bus.publish(
            ConsultaAgendada(
                consulta_id=created.id,
                paciente_id=data.paciente_id,
                medico_id=data.medico_id,
                data_hora=data.data_hora.isoformat(),
            )
        )

        return await self.get_by_id(created.id)

    async def get_by_id(self, consulta_id: int) -> ConsultaResponse:
        consulta = await self.repository.get_by_id(consulta_id)
        if not consulta:
            raise NotFoundException("Consulta não encontrada")
        return ConsultaResponse.model_validate(consulta)

    async def get_by_sala(self, sala_webrtc: str) -> ConsultaResponse:
        consulta = await self.repository.get_by_sala(sala_webrtc)
        if not consulta:
            raise NotFoundException("Consulta não encontrada")
        return ConsultaResponse.model_validate(consulta)

    async def update(
        self,
        consulta_id: int,
        data: ConsultaUpdate,
        current_user: User | None = None,
    ) -> ConsultaResponse:
        consulta = await self.repository.get_by_id(consulta_id)
        if not consulta:
            raise NotFoundException("Consulta não encontrada")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(consulta, field, value)

        updated = await self.repository.update(consulta)
        return await self.get_by_id(updated.id)

    async def delete(self, consulta_id: int) -> None:
        await self.repository.delete(consulta_id)

    async def iniciar(self, consulta_id: int, current_user: User) -> ConsultaResponse:
        consulta = await self.repository.get_by_id(consulta_id)
        if not consulta:
            raise NotFoundException("Consulta não encontrada")

        if consulta.status != StatusConsulta.AGENDADA:
            raise ForbiddenException("Consulta não pode ser iniciada")

        updated = await self.repository.update_status(
            consulta_id,
            StatusConsulta.EM_ANDAMENTO,
            observacao="Consulta iniciada",
            user_id=current_user.id,
        )
        return ConsultaResponse.model_validate(updated)

    async def finalizar(self, consulta_id: int, current_user: User) -> ConsultaResponse:
        consulta = await self.repository.get_by_id(consulta_id)
        if not consulta:
            raise NotFoundException("Consulta não encontrada")

        if consulta.status != StatusConsulta.EM_ANDAMENTO:
            raise ForbiddenException("Consulta não está em andamento")

        updated = await self.repository.update_status(
            consulta_id,
            StatusConsulta.FINALIZADA,
            observacao="Consulta finalizada",
            user_id=current_user.id,
        )
        return ConsultaResponse.model_validate(updated)

    async def cancelar(self, consulta_id: int, current_user: User, observacao: str | None = None) -> ConsultaResponse:
        consulta = await self.repository.get_by_id(consulta_id)
        if not consulta:
            raise NotFoundException("Consulta não encontrada")

        if consulta.status == StatusConsulta.FINALIZADA:
            raise ForbiddenException("Consulta já foi finalizada")

        updated = await self.repository.update_status(
            consulta_id,
            StatusConsulta.CANCELADA,
            observacao=observacao or "Consulta cancelada",
            user_id=current_user.id,
        )
        return ConsultaResponse.model_validate(updated)

    async def search(
        self,
        paciente_id: int | None = None,
        medico_id: int | None = None,
        status: StatusConsulta | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ConsultaSearchResponse:
        consultas, total = await self.repository.search(
            paciente_id=paciente_id,
            medico_id=medico_id,
            status=status,
            data_inicio=data_inicio,
            data_fim=data_fim,
            skip=skip,
            limit=limit,
        )
        return ConsultaSearchResponse(
            total=total,
            consultas=[ConsultaResponse.model_validate(c) for c in consultas],
        )

    async def list_hoje(self, current_user: User) -> list[ConsultaResponse]:
        consultas = await self.repository.list_hoje(
            usuario_id=current_user.id,
            tipo=current_user.tipo.value,
        )
        return [ConsultaResponse.model_validate(c) for c in consultas]
