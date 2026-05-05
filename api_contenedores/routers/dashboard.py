from datetime import date, timedelta
from typing import List
from fastapi import APIRouter, Depends
from collections import Counter
from sqlalchemy.orm import Session

from schemas import DashboardStats, NotificacionItem
from database import get_db
from models import Contenedor, TipoContenedor, Cliente, Arrendamiento, Movimiento
from auth.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

ZONA_MAP = [
    ("cartagena",    "Puerto Cartagena"),
    ("barranquilla", "Barranquilla"),
    ("bogot",        "Bogotá"),
    ("medell",       "Medellín"),
    ("cali",         "Cali"),
    ("bucaramanga",  "Bucaramanga"),
    ("taller",       "Taller/Mantenimiento"),
    ("mantenimiento","Taller/Mantenimiento"),
]

def _get_zona(ubicacion: str | None) -> str:
    if not ubicacion:
        return "Sin zona"
    loc = ubicacion.lower()
    for keyword, nombre in ZONA_MAP:
        if keyword in loc:
            return nombre
    return "Otros"


@router.get("/stats", response_model=DashboardStats,
            summary="Estadísticas generales del sistema")
def get_stats(current=Depends(get_current_user), db: Session = Depends(get_db)):
    contenedores   = db.query(Contenedor).all()
    tipos          = db.query(TipoContenedor).all()
    clientes       = db.query(Cliente).all()
    arrendamientos = db.query(Arrendamiento).all()
    movimientos    = db.query(Movimiento).all()

    tipo_dict    = {t.id_tipo: t.nombre for t in tipos}
    cliente_dict = {cl.id_cliente: cl.nombre for cl in clientes}

    por_estado  = dict(Counter(c.estado        for c in contenedores))
    por_tipo    = dict(Counter(tipo_dict.get(c.id_tipo, "Desconocido")      for c in contenedores))
    por_cliente = dict(Counter(cliente_dict.get(c.id_cliente, "Sin cliente") for c in contenedores))

    hoy    = date.today()
    limit  = hoy + timedelta(days=7)
    activos  = sum(1 for a in arrendamientos if a.estado_arrendamiento == "activo")
    proximos = sum(1 for a in arrendamientos
                   if a.estado_arrendamiento == "activo"
                   and a.fecha_fin and hoy <= a.fecha_fin <= limit)

    return DashboardStats(
        total_contenedores    =len(contenedores),
        por_estado            =por_estado,
        por_tipo              =por_tipo,
        por_cliente           =por_cliente,
        arrendamientos_activos=activos,
        proximos_vencer       =proximos,
        total_movimientos     =len(movimientos),
    )


@router.get("/notificaciones", response_model=List[NotificacionItem],
            summary="Notificaciones generadas del sistema")
def get_notificaciones(current=Depends(get_current_user), db: Session = Depends(get_db)):
    notifs: list[NotificacionItem] = []
    hoy    = date.today()
    limit7 = hoy + timedelta(days=7)

    # Arrendamientos próximos a vencer
    proximos = db.query(Arrendamiento).filter(
        Arrendamiento.estado_arrendamiento == "activo",
        Arrendamiento.fecha_fin >= hoy,
        Arrendamiento.fecha_fin <= limit7
    ).order_by(Arrendamiento.fecha_fin).all()

    clientes_dict = {c.id_cliente: c.nombre for c in db.query(Cliente).all()}
    cont_dict     = {c.id_contenedor: c.id_codigo for c in db.query(Contenedor).all()}

    for a in proximos:
        dias  = (a.fecha_fin - hoy).days
        nivel = "error" if dias <= 2 else "warn"
        notifs.append(NotificacionItem(
            tipo   =nivel,
            titulo =f"Arrendamiento por vencer — {cont_dict.get(a.id_contenedor, '?')}",
            mensaje=f"Cliente: {clientes_dict.get(a.id_cliente, '?')} · Vence en {dias} día{'s' if dias != 1 else ''}",
            fecha  =str(a.fecha_fin),
        ))

    # Últimos 5 movimientos
    movimientos = db.query(Movimiento).order_by(Movimiento.fecha_hora.desc()).limit(5).all()
    for m in movimientos:
        codigo = cont_dict.get(m.id_contenedor, f"#{m.id_contenedor}")
        ruta   = ""
        if m.ubicacion_origen and m.ubicacion_destino:
            ruta = f"{m.ubicacion_origen} → {m.ubicacion_destino}"
        notifs.append(NotificacionItem(
            tipo   ="info",
            titulo =f"Movimiento — {codigo}",
            mensaje=ruta or "Sin detalle de ruta",
            fecha  =m.fecha_hora.strftime("%Y-%m-%d %H:%M") if m.fecha_hora else "",
        ))

    return notifs


@router.get("/zonas/distribucion", summary="Distribución de contenedores por zona")
def get_zonas_distribucion(current=Depends(get_current_user), db: Session = Depends(get_db)):
    contenedores = db.query(Contenedor).all()
    zonas: dict[str, dict] = {}

    for c in contenedores:
        zona = _get_zona(c.ubicacion_actual)
        if zona not in zonas:
            zonas[zona] = {"total": 0, "disponible": 0, "en_transito": 0, "en_patio": 0, "otros": 0}
        zonas[zona]["total"] += 1
        estado = str(c.estado.value) if hasattr(c.estado, "value") else str(c.estado)
        if estado == "disponible":
            zonas[zona]["disponible"] += 1
        elif estado == "en_transito":
            zonas[zona]["en_transito"] += 1
        elif estado == "en_patio":
            zonas[zona]["en_patio"] += 1
        else:
            zonas[zona]["otros"] += 1

    return zonas
