from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import date, datetime
from sqlalchemy.orm import Session

from schemas import FacturacionCreate, FacturacionUpdate, FacturacionOut, AbonoRequest
from database import get_db
from models import Facturacion, Contenedor, Notificacion, Usuario
from auth.dependencies import get_current_user, only_admin
from broadcaster import broadcaster

router = APIRouter(prefix="/facturacion", tags=["Facturación"])


@router.get("/", response_model=List[FacturacionOut], summary="Listar facturas")
def get_facturaciones(
    estado_pago: Optional[str] = Query(None, description="pendiente | pagado | mora"),
    current=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Facturacion)
    if estado_pago:
        q = q.filter(Facturacion.estado_pago == estado_pago)
    return q.order_by(Facturacion.fecha_facturacion.desc()).all()


@router.get("/contenedor/{contenedor_id}", response_model=List[FacturacionOut],
            summary="Facturas de un contenedor")
def get_facturaciones_contenedor(
    contenedor_id: int,
    current=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db.query(Contenedor).filter(Contenedor.id_contenedor == contenedor_id).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    return (db.query(Facturacion)
            .filter(Facturacion.id_contenedor == contenedor_id)
            .order_by(Facturacion.fecha_facturacion)
            .all())


@router.get("/arrendamiento/{arrendamiento_id}", response_model=List[FacturacionOut], summary="Facturas de un arrendamiento")
def get_facturaciones_arrendamiento(
    arrendamiento_id: int,
    current=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Retorna todas las facturas vinculadas a este arrendamiento
    return db.query(Facturacion).filter(Facturacion.id_arrendamiento == arrendamiento_id).order_by(Facturacion.fecha_facturacion).all()


@router.post("/", response_model=FacturacionOut, status_code=status.HTTP_201_CREATED,
             summary="Crear factura")
def create_facturacion(data: FacturacionCreate, admin=Depends(only_admin), db: Session = Depends(get_db)):
    if not db.query(Contenedor).filter(Contenedor.id_contenedor == data.id_contenedor).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    datos = data.model_dump()
    if not datos.get("codigo_factura"):
        count = db.query(Facturacion).count()
        datos["codigo_factura"] = f"FAC-{count + 1:04d}"

    nuevo = Facturacion(**datos, fecha_facturacion=date.today())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    broadcaster.emit("facturacion", {"action": "created", "id": nuevo.id_factura}, exclude_user_id=admin.id_usuario)
    return nuevo


@router.put("/{factura_id}", response_model=FacturacionOut, summary="Actualizar factura")
def update_facturacion(
    factura_id: int,
    data: FacturacionUpdate,
    admin=Depends(only_admin),
    db: Session = Depends(get_db)
):
    f = db.query(Facturacion).filter(Facturacion.id_factura == factura_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(f, field, value)
        
    # Auto-update estado_pago if monto_pagado changed
    if data.monto_pagado is not None:
        if f.monto_pagado >= f.monto:
            f.estado_pago = "pagado"
        elif f.monto_pagado > 0:
            f.estado_pago = "parcial"
        else:
            f.estado_pago = "pendiente"
            
    db.commit()
    db.refresh(f)
    broadcaster.emit("facturacion", {"action": "updated", "id": f.id_factura}, exclude_user_id=admin.id_usuario)
    return f


@router.post("/{factura_id}/abonar", response_model=FacturacionOut, summary="Abonar a factura")
def abonar_factura(
    factura_id: int,
    data: AbonoRequest,
    admin=Depends(only_admin),
    db: Session = Depends(get_db)
):
    f = db.query(Facturacion).filter(Facturacion.id_factura == factura_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    if data.monto <= 0:
        raise HTTPException(status_code=400, detail="El abono debe ser mayor a 0")
    
    faltante = f.monto - f.monto_pagado
    if data.monto > faltante:
        raise HTTPException(status_code=400, detail=f"El abono ({data.monto}) excede el saldo pendiente ({faltante})")
        
    f.monto_pagado += data.monto
    if f.monto_pagado >= f.monto:
        f.monto_pagado = f.monto  # Cap at max
        f.estado_pago = "pagado"
    else:
        f.estado_pago = "parcial"
        
    db.commit()
    db.refresh(f)

    # ── Crear notificación de pago para todos los admin/supervisor ────────
    try:
        es_pago_total = f.estado_pago == "pagado"
        tipo_pago = "Pago completo" if es_pago_total else "Abono parcial"
        codigo = f.codigo_factura or f"FAC-{f.id_factura}"
        monto_fmt = f"${data.monto:,.0f}"
        titulo = f"{tipo_pago} — {codigo}"
        mensaje = (
            f"{monto_fmt} registrado · "
            f"Total pagado: ${f.monto_pagado:,.0f} / ${f.monto:,.0f}"
        )
        if es_pago_total:
            mensaje += " ✓ Factura saldada"

        ref_id = f"pago_{f.id_factura}_{int(datetime.utcnow().timestamp())}"
        nivel = "info" if es_pago_total else "warn"

        destinatarios = (
            db.query(Usuario.id_usuario)
            .filter(Usuario.rol.in_(["admin", "supervisor"]))
            .all()
        )
        for (uid,) in destinatarios:
            db.add(Notificacion(
                id_usuario=uid,
                tipo=nivel,
                titulo=titulo,
                mensaje=mensaje,
                ref_id=ref_id,
            ))
        db.commit()
    except Exception:
        pass  # No bloquear el pago si la notificación falla

    broadcaster.emit("facturacion", {"action": "abono", "id": f.id_factura}, exclude_user_id=admin.id_usuario)
    return f


@router.delete("/{factura_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_facturacion(factura_id: int, admin=Depends(only_admin), db: Session = Depends(get_db)):
    f = db.query(Facturacion).filter(Facturacion.id_factura == factura_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    factura_id_copy = f.id_factura
    db.delete(f)
    db.commit()
    broadcaster.emit("facturacion", {"action": "deleted", "id": factura_id_copy}, exclude_user_id=admin.id_usuario)
