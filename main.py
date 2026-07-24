import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from core.database import init_db
from events.handlers import register_handlers

from domains.auth.router import router as auth_router
from domains.pacientes.router import router as pacientes_router
from domains.medicos.router import router as medicos_router
from domains.medicos.router import router_esp as especialidades_router
from domains.consultas.router import router as consultas_router
from domains.prontuario.router import router as prontuario_router
from domains.receitas.router import router as receitas_router
from domains.receitas.router import router_atest as atestados_router
from domains.webrtc.router import router as webrtc_router
from domains.triagem.router import router as triagem_router
from domains.auditoria.router import router as auditoria_router
from domains.dashboard.router import router as dashboard_router

settings = get_settings()

logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicação...")
    
    # Registrar handlers de eventos
    register_handlers()
    
    # Inicializar banco de dados
    await init_db()
    logger.info("Banco de dados inicializado")
    
    yield
    
    logger.info("Encerrando aplicação...")


app = FastAPI(
    title="Vitalis Telemedicina API",
    description="API REST para sistema de telemedicina",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(auth_router)
app.include_router(pacientes_router)
app.include_router(medicos_router)
app.include_router(especialidades_router)
app.include_router(consultas_router)
app.include_router(prontuario_router)
app.include_router(receitas_router)
app.include_router(atestados_router)
app.include_router(webrtc_router)
app.include_router(triagem_router)
app.include_router(auditoria_router)
app.include_router(dashboard_router)


@app.get("/")
async def root():
    return {
        "app": "Vitalis Telemedicina",
        "version": "1.0.0",
        "status": "online",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
