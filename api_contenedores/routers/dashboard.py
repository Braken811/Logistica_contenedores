import asyncio
from datetime import date, timedelta, datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from collections import Counter
from sqlalchemy.orm import Session

from schemas import DashboardStats, NotificacionItem, MovimientoResumenDash
from database import get_db
from models import Contenedor, TipoContenedor, Cliente, Arrendamiento, Movimiento, Usuario, Facturacion
from auth.dependencies import get_current_user
from auth.jwt import decode_access_token
from broadcaster import broadcaster

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

MESES_ES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
            'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

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

    tipo_dict    = {t.id_tipo: t.nombre for t in tipos}
    cliente_dict = {cl.id_cliente: cl.nombre for cl in clientes}
    cont_dict    = {c.id_contenedor: c.id_codigo for c in contenedores}

    # Conversión explícita de enum a string para compatibilidad con JSON
    por_estado: dict = {}
    for c in contenedores:
        estado_str = c.estado.value if hasattr(c.estado, "value") else str(c.estado)
        por_estado[estado_str] = por_estado.get(estado_str, 0) + 1

    por_tipo    = dict(Counter(tipo_dict.get(c.id_tipo, "Desconocido")       for c in contenedores))
    por_cliente = dict(Counter(cliente_dict.get(c.id_cliente, "Sin cliente") for c in contenedores))

    hoy    = date.today()
    limit  = hoy + timedelta(days=7)
    activos   = sum(1 for a in arrendamientos if a.estado_arrendamiento == "activo")
    total_arr = len(arrendamientos)
    proximos  = sum(1 for a in arrendamientos
                    if a.estado_arrendamiento == "activo"
                    and a.fecha_fin and hoy <= a.fecha_fin <= limit)

    # ── Datos para gráficas ──────────────────────────────────────────────────

    arr_activos     = activos
    arr_finalizados = sum(1 for a in arrendamientos if a.estado_arrendamiento != "activo")

    # Ventana de 6 meses calendario: calcular el inicio del mes más antiguo
    m_inicio = hoy.month - 5
    y_inicio = hoy.year
    if m_inicio <= 0:
        m_inicio += 12
        y_inicio -= 1
    desde = datetime(y_inicio, m_inicio, 1)

    # Inicializar contadores para los 6 meses
    meses_conteo: dict[str, int] = {}
    for i in range(5, -1, -1):
        m = hoy.month - i
        y = hoy.year
        if m <= 0:
            m += 12
            y -= 1
        meses_conteo[f"{y}-{m:02d}"] = 0

    # Sólo traer movimientos del período (consulta eficiente)
    movimientos_chart = (db.query(Movimiento)
                         .filter(Movimiento.fecha_hora >= desde)
                         .all())
    for mv in movimientos_chart:
        if mv.fecha_hora:
            k = f"{mv.fecha_hora.year}-{mv.fecha_hora.month:02d}"
            if k in meses_conteo:
                meses_conteo[k] += 1

    movimientos_por_mes = [
        {"key": k, "label": MESES_ES[int(k[5:7]) - 1], "count": v}
        for k, v in sorted(meses_conteo.items())
    ]

    # Total real de movimientos (sin cargar todos en memoria)
    total_movimientos = db.query(Movimiento).count()

    # Últimos 20 movimientos para la tabla del panel (con código de contenedor)
    ultimos = (db.query(Movimiento)
               .order_by(Movimiento.fecha_hora.desc())
               .limit(20)
               .all())

    ultimos_movimientos = [
        MovimientoResumenDash(
            id_movimiento    =m.id_movimiento,
            id_contenedor    =m.id_contenedor,
            codigo_contenedor=cont_dict.get(m.id_contenedor),
            ubicacion_origen =m.ubicacion_origen,
            ubicacion_destino=m.ubicacion_destino,
            medio_transporte =m.medio_transporte,
            responsable      =m.responsable,
            fecha_hora       =m.fecha_hora.isoformat() if m.fecha_hora else None,
        )
        for m in ultimos
    ]

    return DashboardStats(
        total_contenedores    =len(contenedores),
        por_estado            =por_estado,
        por_tipo              =por_tipo,
        por_cliente           =por_cliente,
        arrendamientos_activos=activos,
        total_arrendamientos  =total_arr,
        proximos_vencer       =proximos,
        total_movimientos     =total_movimientos,
        movimientos_por_mes   =movimientos_por_mes,
        arr_activos           =arr_activos,
        arr_finalizados       =arr_finalizados,
        ultimos_movimientos   =ultimos_movimientos,
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


@router.get("/financiero", summary="Estadísticas financieras del sistema")
def get_financiero(current=Depends(get_current_user), db: Session = Depends(get_db)):
    hoy    = date.today()
    todas  = db.query(Facturacion).all()

    pendientes  = [f for f in todas if f.estado_pago in ("pendiente", "parcial")]
    mora_list   = [f for f in todas if f.estado_pago == "mora"]

    total_pendiente = sum((f.monto or 0) - (f.monto_pagado or 0) for f in pendientes)
    total_mora      = sum((f.monto or 0) - (f.monto_pagado or 0) for f in mora_list)

    # Ingresos del mes: sumar TODO el monto_pagado de TODAS las facturas
    # (refleja el dinero realmente cobrado, independientemente del estado)
    ingresos_total = sum((f.monto_pagado or 0) for f in todas)

    # Ingresos solo del mes actual (facturas creadas este mes que tienen pagos)
    facturas_mes = [
        f for f in todas
        if f.fecha_facturacion
        and f.fecha_facturacion.month == hoy.month
        and f.fecha_facturacion.year  == hoy.year
    ]
    ingresos_mes = sum((f.monto_pagado or 0) for f in facturas_mes)

    # Si no hay facturas del mes actual pero sí hay pagos globales, usar el total
    # Esto evita que se muestre $0 cuando hay datos reales
    ingresos_mostrar = ingresos_mes if ingresos_mes > 0 else ingresos_total

    return {
        "total_clientes":       db.query(Cliente).count(),
        "fact_pendiente_count": len(pendientes),
        "fact_pendiente_monto": total_pendiente,
        "fact_mora_count":      len(mora_list),
        "fact_mora_monto":      total_mora,
        "ingresos_mes":         ingresos_mostrar,
        "ingresos_mes_count":   len(facturas_mes),
        "ingresos_total":       ingresos_total,
        "total_facturas":       len(todas),
    }


@router.get("/events", summary="Stream de eventos en tiempo real (SSE)")
async def sse_events(
    token: str = Query(..., description="JWT de autenticación"),
    db: Session = Depends(get_db),
):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    user = db.query(Usuario).filter(Usuario.user == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user_id: int = user.id_usuario

    async def generator():
        queue = broadcaster.subscribe(user_id)
        try:
            yield "data: {\"type\":\"connected\"}\n\n"
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=25)
                    yield msg
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            broadcaster.unsubscribe(user_id, queue)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
