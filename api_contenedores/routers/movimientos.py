from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from sqlalchemy.orm import Session

from schemas import MovimientoCreate, MovimientoOut
from database import get_db
from models import Movimiento, Contenedor
from auth.dependencies import get_current_user

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])


@router.get("/", response_model=List[MovimientoOut], summary="Listar movimientos")
def get_movimientos(current=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Movimiento).order_by(Movimiento.fecha_hora.desc()).all()


# RF01: Movimientos de un contenedor específico
@router.get("/contenedor/{contenedor_id}", response_model=List[MovimientoOut],
            summary="Movimientos de un contenedor (cronológico)")
def get_movimientos_contenedor(contenedor_id: int, current=Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.query(Contenedor).filter(Contenedor.id_contenedor == contenedor_id).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    return db.query(Movimiento).filter(Movimiento.id_contenedor == contenedor_id).order_by(Movimiento.fecha_hora).all()


@router.post("/", response_model=MovimientoOut, status_code=status.HTTP_201_CREATED,
             summary="Registrar movimiento")
def create_movimiento(data: MovimientoCreate, current=Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.query(Contenedor).filter(Contenedor.id_contenedor == data.id_contenedor).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    nuevo = Movimiento(**data.model_dump(), fecha_hora=datetime.utcnow())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.delete("/{movimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movimiento(movimiento_id: int, current=Depends(get_current_user), db: Session = Depends(get_db)):
    m = db.query(Movimiento).filter(Movimiento.id_movimiento == movimiento_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    db.delete(m)
    db.commit()
