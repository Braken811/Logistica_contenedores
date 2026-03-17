from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from schemas import DashboardStats
from auth_utils import get_current_user
import models

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats,
            summary="Estadísticas generales del sistema")
def get_stats(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    """
    RF07 — Devuelve KPIs consolidados:
    - Total de contenedores
    - Distribución por estado, tipo y cliente
    - Arrendamientos activos y próximos a vencer (≤7 días)
    - Total de movimientos registrados
    """
    # Total
    total = db.query(func.count(models.Contenedor.id_contenedor)).scalar()

    # Por estado
    por_estado_rows = db.query(
        models.Contenedor.estado,
        func.count(models.Contenedor.id_contenedor)
    ).group_by(models.Contenedor.estado).all()
    por_estado = {row[0]: row[1] for row in por_estado_rows}

    # Por tipo
    por_tipo_rows = db.query(
        models.TipoContenedor.nombre,
        func.count(models.Contenedor.id_contenedor)
    ).join(models.TipoContenedor,
           models.Contenedor.id_tipo == models.TipoContenedor.id_tipo
    ).group_by(models.TipoContenedor.nombre).all()
    por_tipo = {row[0]: row[1] for row in por_tipo_rows}

    # Por cliente
    por_cliente_rows = db.query(
        models.Cliente.nombre,
        func.count(models.Contenedor.id_contenedor)
    ).join(models.Cliente,
           models.Contenedor.id_cliente == models.Cliente.id_cliente
    ).group_by(models.Cliente.nombre).all()
    por_cliente = {row[0]: row[1] for row in por_cliente_rows}

    # Arrendamientos activos
    activos = db.query(func.count(models.ArrendamientoContenedor.id_arrendamiento)).filter(
        models.ArrendamientoContenedor.estado_arrendamiento == "activo"
    ).scalar()

    # Próximos a vencer (≤7 días)
    hoy   = date.today()
    limit = hoy + timedelta(days=7)
    proximos = db.query(func.count(models.ArrendamientoContenedor.id_arrendamiento)).filter(
        models.ArrendamientoContenedor.fecha_fin >= hoy,
        models.ArrendamientoContenedor.fecha_fin <= limit,
        models.ArrendamientoContenedor.estado_arrendamiento == "activo"
    ).scalar()

    # Total movimientos
    total_movimientos = db.query(func.count(models.Movimiento.id_movimiento)).scalar()

    return DashboardStats(
        total_contenedores    =total or 0,
        por_estado            =por_estado,
        por_tipo              =por_tipo,
        por_cliente           =por_cliente,
        arrendamientos_activos=activos or 0,
        proximos_vencer       =proximos or 0,
        total_movimientos     =total_movimientos or 0,
    )
