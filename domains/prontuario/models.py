from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base


class Prontuario(Base):
    __tablename__ = "prontuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("pacientes.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    paciente = relationship("Paciente", back_populates="prontuario")
    anotacoes = relationship("Anotacao", back_populates="prontuario", cascade="all, delete-orphan")
    evolucoes = relationship("Evolucao", back_populates="prontuario", cascade="all, delete-orphan")
    exames = relationship("Exame", back_populates="prontuario", cascade="all, delete-orphan")


class Anotacao(Base):
    __tablename__ = "anotacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prontuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("prontuarios.id"), nullable=False)
    consulta_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("consultas.id"))
    medico_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("medicos.id"))
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    prontuario = relationship("Prontuario", back_populates="anotacoes")


class Evolucao(Base):
    __tablename__ = "evolucoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prontuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("prontuarios.id"), nullable=False)
    consulta_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("consultas.id"))
    medico_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("medicos.id"))
    tipo: Mapped[str] = mapped_column(String(50))  # inicial, evolucao, alta
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    prontuario = relationship("Prontuario", back_populates="evolucoes")


class Exame(Base):
    __tablename__ = "exames"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prontuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("prontuarios.id"), nullable=False)
    consulta_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("consultas.id"))
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(String(100))
    resultado: Mapped[str | None] = mapped_column(Text)
    data_solicitacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    data_resultado: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    arquivo_url: Mapped[str | None] = mapped_column(String(500))

    prontuario = relationship("Prontuario", back_populates="exames")
