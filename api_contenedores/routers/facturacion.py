from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import date
from sqlalchemy.orm import Session

from schemas import FacturacionCreate, FacturacionOut
from database import get_db
from models import Facturacion, Contenedor

router = APIRouter(prefix="/facturacion", tags=["Facturación"])


@router.get("/", response_model=List[FacturacionOut], summary="Listar facturaciones")
def get_facturaciones(db: Session = Depends(get_db)):
    return db.query(Facturacion).order_by(Facturacion.fecha_facturacion.desc()).all()


@router.get("/contenedor/{contenedor_id}", response_model=List[FacturacionOut],
            summary="Facturaciones de un contenedor")
def get_facturaciones_contenedor(contenedor_id: int, db: Session = Depends(get_db)):
    if not db.query(Contenedor).filter(Contenedor.id_contenedor == contenedor_id).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    return db.query(Facturacion).filter(Facturacion.id_contenedor == contenedor_id).order_by(Facturacion.fecha_facturacion).all()


@router.post("/", response_model=FacturacionOut, status_code=status.HTTP_201_CREATED,
             summary="Registrar facturación")
def create_facturacion(data: FacturacionCreate, db: Session = Depends(get_db)):
    if not db.query(Contenedor).filter(Contenedor.id_contenedor == data.id_contenedor).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    nuevo = Facturacion(**data.model_dump(), fecha_facturacion=date.today())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.delete("/{factura_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_facturacion(factura_id: int, db: Session = Depends(get_db)):
    f = db.query(Facturacion).filter(Facturacion.id_factura == factura_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    db.delete(f)
    db.commit()
