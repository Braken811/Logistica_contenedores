from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import date
from sqlalchemy.orm import Session

from schemas import VentaCreate, VentaOut
from database import get_db
from models import Venta, Contenedor, Cliente

router = APIRouter(prefix="/ventas", tags=["Ventas"])


@router.get("/", response_model=List[VentaOut], summary="Listar ventas")
def get_ventas(db: Session = Depends(get_db)):
    return db.query(Venta).order_by(Venta.fecha_venta.desc()).all()


@router.get("/{venta_id}", response_model=VentaOut)
def get_venta(venta_id: int, db: Session = Depends(get_db)):
    v = db.query(Venta).filter(Venta.id_venta == venta_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return v


@router.post("/", response_model=VentaOut, status_code=status.HTTP_201_CREATED,
             summary="Registrar venta")
def create_venta(data: VentaCreate, db: Session = Depends(get_db)):
    if not db.query(Contenedor).filter(Contenedor.id_contenedor == data.id_contenedor).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    if not db.query(Cliente).filter(Cliente.id_cliente == data.id_cliente).first():
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    nuevo = Venta(**data.model_dump(), fecha_venta=date.today())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.delete("/{venta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venta(venta_id: int, db: Session = Depends(get_db)):
    v = db.query(Venta).filter(Venta.id_venta == venta_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    db.delete(v)
    db.commit()
