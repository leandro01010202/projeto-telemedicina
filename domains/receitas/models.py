from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base


class Receita(Base):
    __tablename__ = "receitas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("pacientes.id"), nullable=False)
    medico_id: Mapped[int] = mapped_column(Integer, ForeignKey("medicos.id"), nullable=False)
    consulta_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("consultas.id"))
    validade_dias: Mapped[int] = mapped_column(Integer, default=30)  # Validade em dias
    observacoes: Mapped[str | None] = mapped_column(Text)
    esta_assinada: Mapped[bool] = mapped_column(Boolean, default=False)
    assinatura_hash: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    paciente = relationship("Paciente")
    medico = relationship("Medico")
    itens = relationship("ItemReceita", back_populates="receita", cascade="all, delete-orphan")


class ItemReceita(Base):
    __tablename__ = "itens_receita"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    receita_id: Mapped[int] = mapped_column(Integer, ForeignKey("receitas.id"), nullable=False)
    medicamento: Mapped[str] = mapped_column(String(255), nullable=False)
    concentracao: Mapped[str | None] = mapped_column(String(100))
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    posologia: Mapped[str] = mapped_column(Text, nullable=False)  # Ex: "1 comprimido, 3x ao dia"
    via_administracao: Mapped[str | None] = mapped_column(String(50))  # Oral, IV, IM, etc.

    receita = relationship("Receita", back_populates="itens")


class Atestado(Base):
    __tablename__ = "atestados"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("pacientes.id"), nullable=False)
    medico_id: Mapped[int] = mapped_column(Integer, ForeignKey("medicos.id"), nullable=False)
    consulta_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("consultas.id"))
    cid: Mapped[str | None] = mapped_column(String(10))  # CID-10
    dias: Mapped[int] = mapped_column(Integer, nullable=False)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    esta_assinado: Mapped[bool] = mapped_column(Boolean, default=False)
    assinatura_hash: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    paciente = relationship("Paciente")
    medico = relationship("Medico")
