from typing import List
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Notificacion, Arrendamiento, Movimiento, Contenedor, Cliente, Usuario
from schemas import NotificacionOut
from auth.dependencies import get_current_user

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


def _sync_notifications(id_usuario: int, db: Session) -> None:
    """
    Genera notificaciones de sistema para el usuario si aún no existen.
    Usa ref_id como clave estable para evitar duplicados.
    Actualiza el mensaje de arrendamientos no leídos con los días restantes actuales.
    """
    hoy    = date.today()
    limit7 = hoy + timedelta(days=7)

    cont_map     = {c.id_contenedor: c.id_codigo for c in db.query(Contenedor).all()}
    clientes_map = {c.id_cliente: c.nombre for c in db.query(Cliente).all()}

    # ── Arrendamientos próximos a vencer ──────────────────────────────────────
    proximos = (
        db.query(Arrendamiento)
        .filter(
            Arrendamiento.estado_arrendamiento == "activo",
            Arrendamiento.fecha_fin >= hoy,
            Arrendamiento.fecha_fin <= limit7,
        )
        .all()
    )

    for a in proximos:
        dias  = (a.fecha_fin - hoy).days
        nivel = "error" if dias <= 2 else "warn"
        ref   = f"arr_{a.id_arrendamiento}_vencer"
        codigo   = cont_map.get(a.id_contenedor, "?")
        cliente  = clientes_map.get(a.id_cliente, "?")
        mensaje  = f"Cliente: {cliente} · Vence en {dias} día{'s' if dias != 1 else ''}"

        existing = (
            db.query(Notificacion)
            .filter(Notificacion.id_usuario == id_usuario, Notificacion.ref_id == ref)
            .first()
        )
        if not existing:
            db.add(Notificacion(
                id_usuario=id_usuario,
                tipo=nivel,
                titulo=f"Arrendamiento por vencer — {codigo}",
                mensaje=mensaje,
                ref_id=ref,
            ))
        elif not existing.leido:
            existing.tipo    = nivel
            existing.mensaje = mensaje

    # ── Últimos 5 movimientos ─────────────────────────────────────────────────
    movimientos = (
        db.query(Movimiento)
        .order_by(Movimiento.fecha_hora.desc())
        .limit(5)
        .all()
    )

    for m in movimientos:
        ref = f"mov_{m.id_movimiento}"
        already = (
            db.query(Notificacion.id_notificacion)
            .filter(Notificacion.id_usuario == id_usuario, Notificacion.ref_id == ref)
            .first()
        )
        if not already:
            codigo = cont_map.get(m.id_contenedor, f"#{m.id_contenedor}")
            ruta   = (
                f"{m.ubicacion_origen} → {m.ubicacion_destino}"
                if m.ubicacion_origen and m.ubicacion_destino
                else "Sin detalle de ruta"
            )
            db.add(Notificacion(
                id_usuario=id_usuario,
                tipo="info",
                titulo=f"Movimiento — {codigo}",
                mensaje=ruta,
                ref_id=ref,
                fecha=m.fecha_hora or datetime.utcnow(),
            ))

    db.commit()


@router.get("/", response_model=List[NotificacionOut],
            summary="Listar notificaciones del usuario autenticado")
def get_notificaciones(current=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Sincroniza notificaciones de sistema y devuelve las 50 más recientes
    del usuario, ordenadas: no leídas primero, luego por fecha descendente.
    """
    usuario: Usuario = current["user"]
    _sync_notifications(usuario.id_usuario, db)
    return (
        db.query(Notificacion)
        .filter(Notificacion.id_usuario == usuario.id_usuario)
        .order_by(Notificacion.leido.asc(), Notificacion.fecha.desc())
        .limit(50)
        .all()
    )


@router.post("/{notif_id}/read", response_model=NotificacionOut,
             summary="Marcar una notificación como leída")
def mark_read(
    notif_id: int,
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    usuario: Usuario = current["user"]
    n = (
        db.query(Notificacion)
        .filter(
            Notificacion.id_notificacion == notif_id,
            Notificacion.id_usuario == usuario.id_usuario,
        )
        .first()
    )
    if not n:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    if not n.leido:
        n.leido         = True
        n.fecha_lectura = datetime.utcnow()
        db.commit()
        db.refresh(n)
    return n


@router.post("/read-all", summary="Marcar todas las notificaciones del usuario como leídas")
def mark_all_read(current=Depends(get_current_user), db: Session = Depends(get_db)):
    usuario: Usuario = current["user"]
    db.query(Notificacion).filter(
        Notificacion.id_usuario == usuario.id_usuario,
        Notificacion.leido == False,
    ).update({"leido": True, "fecha_lectura": datetime.utcnow()})
    db.commit()
    return {"mensaje": "Todas las notificaciones marcadas como leídas"}


@router.delete("/{notif_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar una notificación")
def delete_notificacion(
    notif_id: int,
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    usuario: Usuario = current["user"]
    n = (
        db.query(Notificacion)
        .filter(
            Notificacion.id_notificacion == notif_id,
            Notificacion.id_usuario == usuario.id_usuario,
        )
        .first()
    )
    if not n:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    db.delete(n)
    db.commit()
