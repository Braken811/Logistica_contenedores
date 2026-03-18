from datetime import date, timedelta
from fastapi import APIRouter, Depends
from collections import Counter
from sqlalchemy.orm import Session

from schemas import DashboardStats
from database import get_db
from models import Contenedor, TipoContenedor, Cliente, Arrendamiento, Movimiento

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats,
            summary="Estadísticas generales del sistema")
def get_stats(db: Session = Depends(get_db)):
    """
    RF07 — Devuelve KPIs consolidados:
    - Total de contenedores
    - Distribución por estado, tipo y cliente
    - Arrendamientos activos y próximos a vencer (≤7 días)
    - Total de movimientos registrados
    """
    contenedores = db.query(Contenedor).all()
    tipos = db.query(TipoContenedor).all()
    clientes = db.query(Cliente).all()
    arrendamientos = db.query(Arrendamiento).all()
    movimientos = db.query(Movimiento).all()

    # Total
    total = len(contenedores)

    # Por estado
    por_estado = Counter(c.estado for c in contenedores)

    # Por tipo
    tipo_dict = {t.id_tipo: t.nombre for t in tipos}
    por_tipo = Counter(tipo_dict.get(c.id_tipo, "Desconocido") for c in contenedores)

    # Por cliente
    cliente_dict = {cl.id_cliente: cl.nombre for cl in clientes}
    por_cliente = Counter(cliente_dict.get(c.id_cliente, "Desconocido") for c in contenedores)

    # Arrendamientos activos
    activos = sum(1 for a in arrendamientos if a.estado_arrendamiento == "activo")

    # Próximos a vencer (≤7 días)
    hoy = date.today()
    limit = hoy + timedelta(days=7)
    proximos = sum(1 for a in arrendamientos if a.estado_arrendamiento == "activo" and a.fecha_fin and hoy <= a.fecha_fin <= limit)

    # Total movimientos
    total_movimientos = len(movimientos)

    return DashboardStats(
        total_contenedores    =total,
        por_estado            =dict(por_estado),
        por_tipo              =dict(por_tipo),
        por_cliente           =dict(por_cliente),
        arrendamientos_activos=activos,
        proximos_vencer       =proximos,
        total_movimientos     =total_movimientos,
    )
