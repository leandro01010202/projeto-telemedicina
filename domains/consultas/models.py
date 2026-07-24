from datetime import datetime
from enum import Enum
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base


class StatusConsulta(str, Enum):
    AGENDADA = "agendada"
    EM_ANDAMENTO = "em_andamento"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"


class Consulta(Base):
    __tablename__ = "consultas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("pacientes.id"), nullable=False)
    medico_id: Mapped[int] = mapped_column(Integer, ForeignKey("medicos.id"), nullable=False)
    data_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duracao_minutos: Mapped[int] = mapped_column(Integer, default=30)
    status: Mapped[StatusConsulta] = mapped_column(
        SQLEnum(StatusConsulta), default=StatusConsulta.AGENDADA
    )
    motivo: Mapped[str | None] = mapped_column(Text)
    sala_webrtc: Mapped[str | None] = mapped_column(String(100))  # ID único da sala
    data_inicio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    data_fim: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    paciente = relationship("Paciente", back_populates="consultas")
    medico = relationship("Medico", back_populates="consultas", foreign_keys=[medico_id])
    triagem = relationship("Triagem", back_populates="consulta", uselist=False)
    prontuario = relationship("Prontuario", back_populates="consulta", uselist=False)
    historico = relationship("StatusHistorico", back_populates="consulta", cascade="all, delete-orphan")


class StatusHistorico(Base):
    __tablename__ = "status_historico"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    consulta_id: Mapped[int] = mapped_column(Integer, ForeignKey("consultas.id"), nullable=False)
    status_anterior: Mapped[str | None] = mapped_column(String(50))
    status_novo: Mapped[str] = mapped_column(String(50), nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text)
    alterado_por: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    consulta = relationship("Consulta", back_populates="historico")
