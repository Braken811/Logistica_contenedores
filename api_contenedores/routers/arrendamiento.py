from typing import List
from datetime import date, timedelta
from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlalchemy.orm import Session

from schemas import ArrendamientoCreate, ArrendamientoUpdate, ArrendamientoOut
from database import get_db
from models import Arrendamiento, Contenedor, Cliente
from auth.dependencies import only_admin

router = APIRouter(prefix="/arrendamientos", tags=["Arrendamientos"])


@router.get("/", response_model=List[ArrendamientoOut], summary="Listar arrendamientos")
def get_arrendamientos(admin=Depends(only_admin), db: Session = Depends(get_db)):
    return db.query(Arrendamiento).all()


# RF09: Alertas de próximo vencimiento
@router.get("/proximos-vencer", response_model=List[ArrendamientoOut],
            summary="Arrendamientos próximos a vencer")
def get_proximos_vencer(dias: int = Query(7, ge=1, le=90, description="Días de anticipación para la alerta"), admin=Depends(only_admin), db: Session = Depends(get_db)):
    """
    Devuelve los arrendamientos activos cuya fecha_fin
    está dentro de los próximos `dias` días.
    """
    hoy = date.today()
    limit = hoy + timedelta(days=dias)
    return db.query(Arrendamiento).filter(
        Arrendamiento.estado_arrendamiento == "activo",
        Arrendamiento.fecha_fin >= hoy,
        Arrendamiento.fecha_fin <= limit
    ).all()


@router.get("/{arrendamiento_id}", response_model=ArrendamientoOut)
def get_arrendamiento(arrendamiento_id: int, admin=Depends(only_admin), db: Session = Depends(get_db)):
    a = db.query(Arrendamiento).filter(Arrendamiento.id_arrendamiento == arrendamiento_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Arrendamiento no encontrado")
    return a


@router.post("/", response_model=ArrendamientoOut, status_code=status.HTTP_201_CREATED,
             summary="Registrar arrendamiento")
def create_arrendamiento(data: ArrendamientoCreate, admin=Depends(only_admin), db: Session = Depends(get_db)):
    if not db.query(Contenedor).filter(Contenedor.id_contenedor == data.id_contenedor).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    if not db.query(Cliente).filter(Cliente.id_cliente == data.id_cliente).first():
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    nuevo = Arrendamiento(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{arrendamiento_id}", response_model=ArrendamientoOut,
            summary="Actualizar arrendamiento")
def update_arrendamiento(arrendamiento_id: int, data: ArrendamientoUpdate, admin=Depends(only_admin), db: Session = Depends(get_db)):
    a = db.query(Arrendamiento).filter(Arrendamiento.id_arrendamiento == arrendamiento_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Arrendamiento no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(a, field, value)
    db.commit()
    db.refresh(a)
    return a


@router.delete("/{arrendamiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_arrendamiento(arrendamiento_id: int, admin=Depends(only_admin), db: Session = Depends(get_db)):
    a = db.query(Arrendamiento).filter(Arrendamiento.id_arrendamiento == arrendamiento_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Arrendamiento no encontrado")
    db.delete(a)
    db.commit()
