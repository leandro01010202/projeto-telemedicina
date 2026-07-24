from domains.dashboard.service import DashboardService, DashboardStats, ConsultasPorDia
from domains.dashboard.router import router as dashboard_router

__all__ = [
    "DashboardService",
    "DashboardStats",
    "ConsultasPorDia",
    "dashboard_router",
]
