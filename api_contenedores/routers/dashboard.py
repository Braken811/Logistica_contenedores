from datetime import date, timedelta
from fastapi import APIRouter
from collections import Counter

from schemas import DashboardStats
from data_utils import load_data

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats,
            summary="Estadísticas generales del sistema")
def get_stats():
    """
    RF07 — Devuelve KPIs consolidados:
    - Total de contenedores
    - Distribución por estado, tipo y cliente
    - Arrendamientos activos y próximos a vencer (≤7 días)
    - Total de movimientos registrados
    """
    contenedores = load_data("contenedores.json")
    tipos = load_data("tipos_contenedores.json")
    clientes = load_data("clientes.json")
    arrendamientos = load_data("arrendamiento.json")
    movimientos = load_data("movimientos.json")

    # Total
    total = len(contenedores)

    # Por estado
    por_estado = Counter(c["estado"] for c in contenedores)

    # Por tipo
    tipo_dict = {t["id_tipo"]: t["nombre"] for t in tipos}
    por_tipo = Counter(tipo_dict.get(c["id_tipo"], "Desconocido") for c in contenedores)

    # Por cliente
    cliente_dict = {cl["id_cliente"]: cl["nombre"] for cl in clientes}
    por_cliente = Counter(cliente_dict.get(c["id_cliente"], "Desconocido") for c in contenedores)

    # Arrendamientos activos
    activos = sum(1 for a in arrendamientos if a.get("estado_arrendamiento") == "activo")

    # Próximos a vencer (≤7 días)
    hoy = date.today()
    limit = hoy + timedelta(days=7)
    proximos = sum(1 for a in arrendamientos if a.get("estado_arrendamiento") == "activo" and hoy <= date.fromisoformat(a["fecha_fin"]) <= limit)

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
