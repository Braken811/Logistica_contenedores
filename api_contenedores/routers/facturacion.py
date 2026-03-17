from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import FacturacionCreate, FacturacionOut
from auth_utils import get_current_user, require_admin
import models

router = APIRouter(prefix="/facturacion", tags=["Facturación"])


@router.get("/", response_model=List[FacturacionOut], summary="Listar facturaciones")
def get_facturaciones(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    return db.query(models.Facturacion).order_by(
        models.Facturacion.fecha_facturacion.desc()
    ).all()


@router.get("/contenedor/{contenedor_id}", response_model=List[FacturacionOut],
            summary="Facturaciones de un contenedor")
def get_facturaciones_contenedor(
    contenedor_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    return db.query(models.Facturacion).filter(
        models.Facturacion.id_contenedor == contenedor_id
    ).order_by(models.Facturacion.fecha_facturacion).all()


@router.post("/", response_model=FacturacionOut, status_code=status.HTTP_201_CREATED,
             summary="Registrar facturación")
def create_facturacion(
    data: FacturacionCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    nuevo = models.Facturacion(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.delete("/{factura_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_facturacion(
    factura_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    f = db.query(models.Facturacion).filter(
        models.Facturacion.id_factura == factura_id
    ).first()
    if not f:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    db.delete(f)
    db.commit()
