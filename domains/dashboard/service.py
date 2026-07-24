from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domains.consultas.models import Consulta, StatusConsulta
from domains.consultas.repository import ConsultaRepository


class DashboardStats(BaseModel):
    total_consultas: int
    consultas_hoje: int
    consultas_agendadas: int
    consultas_em_andamento: int
    consultas_finalizadas: int
    consultas_canceladas: int
    medicos_ativos: int
    pacientes_cadastrados: int


class ConsultasPorDia(BaseModel):
    data: str
    total: int


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.consulta_repository = ConsultaRepository(db)

    async def get_stats(self) -> DashboardStats:
        # Total de consultas
        total_result = await self.db.execute(select(func.count(Consulta.id)))
        total_consultas = total_result.scalar() or 0

        # Consultas de hoje
        hoje = datetime.now().date()
        data_inicio = datetime.combine(hoje, datetime.min.time())
        data_fim = datetime.combine(hoje, datetime.max.time())
        
        hoje_result = await self.db.execute(
            select(func.count(Consulta.id)).where(
                Consulta.data_hora >= data_inicio,
                Consulta.data_hora <= data_fim,
            )
        )
        consultas_hoje = hoje_result.scalar() or 0

        # Contagem por status
        status_counts = await self.consulta_repository.count_by_status()

        # Contar médicos ativos
        from domains.medicos.models import Medico
        medicos_result = await self.db.execute(
            select(func.count(Medico.id)).where(Medico.is_ativo == True)
        )
        medicos_ativos = medicos_result.scalar() or 0

        # Contar pacientes
        from domains.pacientes.models import Paciente
        pacientes_result = await self.db.execute(select(func.count(Paciente.id)))
        pacientes_cadastrados = pacientes_result.scalar() or 0

        return DashboardStats(
            total_consultas=total_consultas,
            consultas_hoje=consultas_hoje,
            consultas_agendadas=status_counts.get(StatusConsulta.AGENDADA.value, 0),
            consultas_em_andamento=status_counts.get(StatusConsulta.EM_ANDAMENTO.value, 0),
            consultas_finalizadas=status_counts.get(StatusConsulta.FINALIZADA.value, 0),
            consultas_canceladas=status_counts.get(StatusConsulta.CANCELADA.value, 0),
            medicos_ativos=medicos_ativos,
            pacientes_cadastrados=pacientes_cadastrados,
        )

    async def get_consultas_por_dia(self, dias: int = 30) -> list[ConsultasPorDia]:
        results = []
        
        for i in range(dias):
            data = datetime.now().date() - timedelta(days=i)
            data_inicio = datetime.combine(data, datetime.min.time())
            data_fim = datetime.combine(data, datetime.max.time())
            
            count_result = await self.db.execute(
                select(func.count(Consulta.id)).where(
                    Consulta.data_hora >= data_inicio,
                    Consulta.data_hora <= data_fim,
                )
            )
            count = count_result.scalar() or 0
            
            results.append(ConsultasPorDia(data=data.isoformat(), total=count))
        
        return list(reversed(results))
