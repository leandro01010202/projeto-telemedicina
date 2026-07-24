from dataclasses import dataclass
from datetime import datetime


@dataclass
class Event:
    pass


@dataclass
class ConsultaAgendada(Event):
    consulta_id: int
    paciente_id: int
    medico_id: int
    data_hora: str


@dataclass
class ConsultaIniciada(Event):
    consulta_id: int
    sala_webrtc: str


@dataclass
class ConsultaFinalizada(Event):
    consulta_id: int
    duracao_minutos: int | None


@dataclass
class ConsultaCancelada(Event):
    consulta_id: int
    motivo: str | None


@dataclass
class TriagemRealizada(Event):
    consulta_id: int
    paciente_id: int


@dataclass
class ProntuarioAtualizado(Event):
    consulta_id: int
    paciente_id: int


@dataclass
class ReceitaAssinada(Event):
    receita_id: int
    consulta_id: int
