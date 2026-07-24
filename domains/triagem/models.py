from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database import Base


class Triagem(Base):
    __tablename__ = "triagens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    consulta_id: Mapped[int] = mapped_column(Integer, ForeignKey("consultas.id"), unique=True)
    paciente_id: Mapped[int] = mapped_column(Integer, ForeignKey("pacientes.id"), nullable=False)
    
    # Sinais vitais
    pressao_sistolica: Mapped[int | None] = mapped_column(Integer)
    pressao_distolica: Mapped[int | None] = mapped_column(Integer)
    frequencia_cardiaca: Mapped[int | None] = mapped_column(Integer)
    temperatura: Mapped[float | None] = mapped_column(Float)
    saturacao_oxigenio: Mapped[int | None] = mapped_column(Integer)
    frequencia_respiratoria: Mapped[int | None] = mapped_column(Integer)
    
    # Avaliação
    peso: Mapped[float | None] = mapped_column(Float)
    altura: Mapped[float | None] = mapped_column(Float)
    escala_dor: Mapped[int | None] = mapped_column(Integer)  # 0-10
    queixas: Mapped[str | None] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    consulta = relationship("Consulta", back_populates="triagem")
