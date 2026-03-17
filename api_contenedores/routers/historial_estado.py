# routers/historial_estado.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import HistorialEstadoCreate, HistorialEstadoOut
from auth_utils import get_current_user
import models

router = APIRouter(prefix="/historial-estado", tags=["Historial de Estado"])


@router.get("/contenedor/{contenedor_id}", response_model=List[HistorialEstadoOut])
def get_historial(
    contenedor_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    return db.query(models.HistorialEstado).filter(
        models.HistorialEstado.id_contenedor == contenedor_id
    ).order_by(models.HistorialEstado.fecha_inicio).all()


@router.post("/", response_model=HistorialEstadoOut, status_code=status.HTTP_201_CREATED)
def create_historial(
    data: HistorialEstadoCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    nuevo = models.HistorialEstado(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo
