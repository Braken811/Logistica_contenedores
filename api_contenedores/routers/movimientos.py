from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import MovimientoCreate, MovimientoOut
from auth_utils import get_current_user
import models

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])


@router.get("/", response_model=List[MovimientoOut], summary="Listar movimientos")
def get_movimientos(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    return db.query(models.Movimiento).order_by(models.Movimiento.fecha_hora.desc()).all()


# RF01: Movimientos de un contenedor específico
@router.get("/contenedor/{contenedor_id}", response_model=List[MovimientoOut],
            summary="Movimientos de un contenedor (cronológico)")
def get_movimientos_contenedor(
    contenedor_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    c = db.query(models.Contenedor).filter(
        models.Contenedor.id_contenedor == contenedor_id
    ).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    return db.query(models.Movimiento).filter(
        models.Movimiento.id_contenedor == contenedor_id
    ).order_by(models.Movimiento.fecha_hora).all()


@router.post("/", response_model=MovimientoOut, status_code=status.HTTP_201_CREATED,
             summary="Registrar movimiento")
def create_movimiento(
    data: MovimientoCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    if not db.query(models.Contenedor).filter(
        models.Contenedor.id_contenedor == data.id_contenedor
    ).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    nuevo = models.Movimiento(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.delete("/{movimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    m = db.query(models.Movimiento).filter(
        models.Movimiento.id_movimiento == movimiento_id
    ).first()
    if not m:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    db.delete(m)
    db.commit()
