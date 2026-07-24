import logging
from events.bus import event_bus
from events.events import (
    ConsultaAgendada,
    ConsultaIniciada,
    ConsultaFinalizada,
    TriagemRealizada,
)

logger = logging.getLogger(__name__)


@event_bus.on(ConsultaAgendada)
async def on_consulta_agendada(event: ConsultaAgendada):
    logger.info(f"Consulta {event.consulta_id} agendada para {event.data_hora}")
    # Aqui você pode:
    # - Notificar paciente por email/SMS
    # - Criar sala WebRTC vazia
    # - Adicionar ao calendário
    pass


@event_bus.on(ConsultaIniciada)
async def on_consulta_iniciada(event: ConsultaIniciada):
    logger.info(f"Consulta {event.consulta_id} iniciada, sala {event.sala_webrtc}")
    # Aqui você pode:
    # - Log de auditoria
    # - Notificar spectator se houver
    pass


@event_bus.on(ConsultaFinalizada)
async def on_consulta_finalizada(event: ConsultaFinalizada):
    logger.info(f"Consulta {event.consulta_id} finalizada")
    # Aqui você pode:
    # - Liberar sala WebRTC
    # - Enviar pesquisa de satisfação
    # - Atualizar métricas
    pass


@event_bus.on(TriagemRealizada)
async def on_triagem_realizada(event: TriagemRealizada):
    logger.info(f"Triagem realizada para paciente {event.paciente_id}")
    # Aqui você pode:
    # - Atualizar prontuário
    # - Notificar médico
    pass


def register_handlers() -> None:
    """Função para garantir que os handlers sejam registrados."""
    pass
