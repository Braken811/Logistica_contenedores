from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import date
from sqlalchemy.orm import Session

from schemas import FacturacionCreate, FacturacionUpdate, FacturacionOut
from database import get_db
from models import Facturacion, Contenedor
from auth.dependencies import get_current_user, only_admin

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
    db.commit()
    db.refresh(f)
    return f


@router.delete("/{factura_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_facturacion(factura_id: int, admin=Depends(only_admin), db: Session = Depends(get_db)):
    f = db.query(Facturacion).filter(Facturacion.id_factura == factura_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    db.delete(f)
    db.commit()
