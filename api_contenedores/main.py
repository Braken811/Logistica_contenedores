from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import usuarios, clientes, tipos_contenedores, contenedores
from routers import movimientos, historial_estado, fotos, facturacion
from routers import arrendamiento, ventas, dashboard
from routers import auth

app = FastAPI(
    title="API - Sistema de Logística y Monitoreo de Multiples Contenedores",
    description="API REST para gestión, control y monitoreo de contenedores logísticos. Proyecto Talento Tech 2026/01.",
    version="1.0.0",
    contact={"name": "Talento Tech 2026"},
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


@app.get("/", tags=["Root"])
def root():
    return {
        "sistema": "Logística y Monitoreo de Contenedores",
        "version": "1.0.0",
        "docs": "/docs",
        "estado": "activo",
    }
