from typing import List
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import ArrendamientoCreate, ArrendamientoUpdate, ArrendamientoOut
from auth_utils import get_current_user, require_admin
import models

router = APIRouter(prefix="/arrendamientos", tags=["Arrendamientos"])


@router.get("/", response_model=List[ArrendamientoOut], summary="Listar arrendamientos")
def get_arrendamientos(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    return db.query(models.ArrendamientoContenedor).all()


# RF09: Alertas de próximo vencimiento
@router.get("/proximos-vencer", response_model=List[ArrendamientoOut],
            summary="Arrendamientos próximos a vencer")
def get_proximos_vencer(
    dias: int = Query(7, ge=1, le=90, description="Días de anticipación para la alerta"),
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    """
    Devuelve los arrendamientos activos cuya fecha_fin
    está dentro de los próximos `dias` días.
    """
    hoy   = date.today()
    limit = hoy + timedelta(days=dias)
    return db.query(models.ArrendamientoContenedor).filter(
        models.ArrendamientoContenedor.fecha_fin >= hoy,
        models.ArrendamientoContenedor.fecha_fin <= limit,
        models.ArrendamientoContenedor.estado_arrendamiento == "activo"
    ).all()


@router.get("/{arrendamiento_id}", response_model=ArrendamientoOut)
def get_arrendamiento(
    arrendamiento_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    a = db.query(models.ArrendamientoContenedor).filter(
        models.ArrendamientoContenedor.id_arrendamiento == arrendamiento_id
    ).first()
    if not a:
        raise HTTPException(status_code=404, detail="Arrendamiento no encontrado")
    return a


@router.post("/", response_model=ArrendamientoOut, status_code=status.HTTP_201_CREATED,
             summary="Registrar arrendamiento")
def create_arrendamiento(
    data: ArrendamientoCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    nuevo = models.ArrendamientoContenedor(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{arrendamiento_id}", response_model=ArrendamientoOut,
            summary="Actualizar arrendamiento")
def update_arrendamiento(
    arrendamiento_id: int,
    data: ArrendamientoUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    a = db.query(models.ArrendamientoContenedor).filter(
        models.ArrendamientoContenedor.id_arrendamiento == arrendamiento_id
    ).first()
    if not a:
        raise HTTPException(status_code=404, detail="Arrendamiento no encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(a, field, value)

    db.commit()
    db.refresh(a)
    return a


@router.delete("/{arrendamiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_arrendamiento(
    arrendamiento_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    a = db.query(models.ArrendamientoContenedor).filter(
        models.ArrendamientoContenedor.id_arrendamiento == arrendamiento_id
    ).first()
    if not a:
        raise HTTPException(status_code=404, detail="Arrendamiento no encontrado")
    db.delete(a)
    db.commit()
