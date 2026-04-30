from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles 
from contextlib import asynccontextmanager
import logging

from routers import usuarios, clientes, tipos_contenedores, contenedores
from routers import movimientos, historial_estado, fotos, facturacion
from routers import arrendamiento, ventas, dashboard
from routers import auth
from database import engine, Base
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Lifespan para inicialización
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("\n" + "="*70)
    logger.info("🚀 INICIANDO API - Sistema de Logística de Contenedores")
    logger.info("="*70)
    
    try:
        # Verificar conexión a BD
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            logger.info(f"✅ PostgreSQL conectado: {version.split(',')[0]}")
            
            # Crear todas las tablas
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Tablas de BD inicializadas")
    except Exception as e:
        logger.error(f"❌ Error en startup: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("\n🛑 Deteniendo API")

app = FastAPI(
    title="API - Sistema de Logística y Monitoreo de Multiples Contenedores",
    description="API REST para gestión, control y monitoreo de contenedores logísticos. Proyecto Talento Tech 2026/01.",
    version="1.0.0",
    contact={"name": "Talento Tech 2026"},
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(usuarios.router)
app.include_router(clientes.router)
app.include_router(tipos_contenedores.router)
app.include_router(contenedores.router)
app.include_router(movimientos.router)
app.include_router(historial_estado.router)
app.include_router(fotos.router)
app.include_router(facturacion.router)
app.include_router(arrendamiento.router)
app.include_router(ventas.router)
app.include_router(dashboard.router)
app.include_router(auth.router)

# ── Servir archivos estáticos ────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static", html=False), name="static")


@app.get("/", tags=["Root"])
def root():
    return {
        "sistema": "Logística y Monitoreo de Contenedores",
        "version": "1.0.0",
        "docs": "/docs",
        "estado": "activo",
        "autenticacion": "JWT Bearer Token requerido para la mayoría de endpoints",
    }

@app.get("/login", response_class=FileResponse, tags=["Autenticación"])
async def login():
    response = FileResponse("login.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/dashboard", response_class=FileResponse, tags=["Dashboard"])
async def dashboard_page():
    response = FileResponse("dashboard.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

