from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base


class Especialidade(Base):
    __tablename__ = "especialidades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    medicos = relationship("Medico", back_populates="especialidade")


class Medico(Base):
    __tablename__ = "medicos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True)
    crm: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    crm_estado: Mapped[str] = mapped_column(String(2), nullable=False)
    especialidade_id: Mapped[int] = mapped_column(Integer, ForeignKey("especialidades.id"))
    telefone: Mapped[str | None] = mapped_column(String(20))
    cpf: Mapped[str] = mapped_column(String(14), unique=True, nullable=False)
    data_nascimento: Mapped[datetime | None] = mapped_column(DateTime)
    is_ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    tempo_consulta_minutos: Mapped[int] = mapped_column(Integer, default=30)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="medico")
    especialidade = relationship("Especialidade", back_populates="medicos")
    agenda = relationship("AgendaMedico", back_populates="medico", cascade="all, delete-orphan")
    consultas = relationship("Consulta", back_populates="medico", foreign_keys="Consulta.medico_id")


class AgendaMedico(Base):
    __tablename__ = "agendas_medicos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medico_id: Mapped[int] = mapped_column(Integer, ForeignKey("medicos.id"), nullable=False)
    dia_semana: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Segunda, 6=Domingo
    hora_inicio: Mapped[str] = mapped_column(String(5), nullable=False)  # HH:MM
    hora_fim: Mapped[str] = mapped_column(String(5), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    medico = relationship("Medico", back_populates="agenda")
