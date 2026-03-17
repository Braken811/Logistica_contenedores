from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import VentaCreate, VentaOut
from auth_utils import get_current_user, require_admin
import models

router = APIRouter(prefix="/ventas", tags=["Ventas"])


@router.get("/", response_model=List[VentaOut], summary="Listar ventas")
def get_ventas(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    return db.query(models.VentaContenedor).order_by(
        models.VentaContenedor.fecha_venta.desc()
    ).all()


@router.get("/{venta_id}", response_model=VentaOut)
def get_venta(
    venta_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    v = db.query(models.VentaContenedor).filter(
        models.VentaContenedor.id_venta == venta_id
    ).first()
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return v


@router.post("/", response_model=VentaOut, status_code=status.HTTP_201_CREATED,
             summary="Registrar venta")
def create_venta(
    data: VentaCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    nuevo = models.VentaContenedor(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.delete("/{venta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venta(
    venta_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    v = db.query(models.VentaContenedor).filter(
        models.VentaContenedor.id_venta == venta_id
    ).first()
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    db.delete(v)
    db.commit()
