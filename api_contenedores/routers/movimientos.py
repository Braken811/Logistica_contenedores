from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import datetime, date
from sqlalchemy.orm import Session

from schemas import MovimientoCreate, MovimientoOut
from database import get_db
from models import Movimiento, Contenedor
from auth.dependencies import get_current_user, only_admin

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])


@router.get("/", response_model=List[MovimientoOut], summary="Listar movimientos")
def get_movimientos(
    id_contenedor: Optional[int] = Query(None, description="Filtrar por contenedor"),
    fecha_inicio : Optional[date] = Query(None, description="Fecha inicio (YYYY-MM-DD)"),
    fecha_fin    : Optional[date] = Query(None, description="Fecha fin (YYYY-MM-DD)"),
    skip         : int = Query(0, ge=0),
    limit        : int = Query(100, le=500),
    current=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Movimiento)
    if id_contenedor:
        q = q.filter(Movimiento.id_contenedor == id_contenedor)
    if fecha_inicio:
        q = q.filter(Movimiento.fecha_hora >= datetime.combine(fecha_inicio, datetime.min.time()))
    if fecha_fin:
        q = q.filter(Movimiento.fecha_hora <= datetime.combine(fecha_fin, datetime.max.time()))
    return q.order_by(Movimiento.fecha_hora.desc()).offset(skip).limit(limit).all()


@router.get("/contenedor/{contenedor_id}", response_model=List[MovimientoOut],
            summary="Movimientos de un contenedor (cronológico)")
def get_movimientos_contenedor(
    contenedor_id: int,
    current=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db.query(Contenedor).filter(Contenedor.id_contenedor == contenedor_id).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    return (db.query(Movimiento)
            .filter(Movimiento.id_contenedor == contenedor_id)
            .order_by(Movimiento.fecha_hora)
            .all())


@router.post("/", response_model=MovimientoOut, status_code=status.HTTP_201_CREATED,
             summary="Registrar movimiento")
def create_movimiento(
    data: MovimientoCreate,
    current=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not db.query(Contenedor).filter(Contenedor.id_contenedor == data.id_contenedor).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    nuevo = Movimiento(**data.model_dump(), fecha_hora=datetime.utcnow())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.delete("/{movimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movimiento(
    movimiento_id: int,
    admin=Depends(only_admin),
    db: Session = Depends(get_db)
):
    m = db.query(Movimiento).filter(Movimiento.id_movimiento == movimiento_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    db.delete(m)
    db.commit()
