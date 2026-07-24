from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), unique=True)
    cpf: Mapped[str] = mapped_column(String(14), unique=True, index=True)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    telefone: Mapped[str] = mapped_column(String(20))
    sexo: Mapped[str] = mapped_column(String(1))  # M, F, O
    endereco: Mapped[str] = mapped_column(String(500))
    cidade: Mapped[str] = mapped_column(String(100))
    estado: Mapped[str] = mapped_column(String(2))
    cep: Mapped[str] = mapped_column(String(10))
    observacoes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    user = relationship("User", back_populates="paciente", uselist=False)
    alergias = relationship("Alergia", back_populates="paciente", cascade="all, delete-orphan")
    comorbidades = relationship("Comorbidade", back_populates="paciente", cascade="all, delete-orphan")
    consultas = relationship("Consulta", back_populates="paciente", foreign_keys="Consulta.paciente_id")
    prontuario = relationship("Prontuario", back_populates="paciente", uselist=False)


class Alergia(Base):
    __tablename__ = "alergias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("pacientes.id"), nullable=False)
    sustancia: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_reacao: Mapped[str | None] = mapped_column(String(255))
    gravidade: Mapped[str] = mapped_column(String(20), default="leve")  # leve, moderada, grave
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    paciente = relationship("Paciente", back_populates="alergias")


class Comorbidade(Base):
    __tablename__ = "comorbidades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("pacientes.id"), nullable=False)
    condicao: Mapped[str] = mapped_column(String(255), nullable=False)
    diagnostico_data: Mapped[date | None] = mapped_column(Date)
    em_tratamento: Mapped[bool] = mapped_column(Boolean, default=True)
    observacoes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    paciente = relationship("Paciente", back_populates="comorbidades")
