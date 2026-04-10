# routers/historial_estado.py
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from schemas import HistorialEstadoCreate, HistorialEstadoOut
from database import get_db
from models import HistorialEstado, Contenedor
from auth.dependencies import get_current_user

router = APIRouter(prefix="/historial-estado", tags=["Historial de Estado"])


@router.get("/contenedor/{contenedor_id}", response_model=List[HistorialEstadoOut])
def get_historial(contenedor_id: int, current=Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.query(Contenedor).filter(Contenedor.id_contenedor == contenedor_id).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    return db.query(HistorialEstado).filter(HistorialEstado.id_contenedor == contenedor_id).order_by(HistorialEstado.fecha_inicio).all()


@router.post("/", response_model=HistorialEstadoOut, status_code=status.HTTP_201_CREATED)
def create_historial(data: HistorialEstadoCreate, current=Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.query(Contenedor).filter(Contenedor.id_contenedor == data.id_contenedor).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    nuevo = HistorialEstado(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo
