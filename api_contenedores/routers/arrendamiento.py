from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlalchemy.orm import Session

from schemas import ArrendamientoCreate, ArrendamientoUpdate, ArrendamientoOut
from database import get_db
from models import Arrendamiento, Contenedor, Cliente
from auth.dependencies import get_current_user, only_admin, only_admin_or_supervisor
from broadcaster import broadcaster

router = APIRouter(prefix="/arrendamientos", tags=["Arrendamientos"])


@router.get("/", response_model=List[ArrendamientoOut], summary="Listar arrendamientos")
def get_arrendamientos(
    estado: Optional[str] = Query(None, description="activo | finalizado"),
    current=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Arrendamiento)
    if estado:
        q = q.filter(Arrendamiento.estado_arrendamiento == estado)
    return q.order_by(Arrendamiento.fecha_inicio.desc()).all()


@router.get("/proximos-vencer", response_model=List[ArrendamientoOut],
            summary="Arrendamientos próximos a vencer")
def get_proximos_vencer(
    dias: int = Query(7, ge=1, le=90),
    current=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    hoy   = date.today()
    limit = hoy + timedelta(days=dias)
    return (db.query(Arrendamiento)
            .filter(
                Arrendamiento.estado_arrendamiento == "activo",
                Arrendamiento.fecha_fin >= hoy,
                Arrendamiento.fecha_fin <= limit
            ).all())


@router.get("/{arrendamiento_id}", response_model=ArrendamientoOut)
def get_arrendamiento(
    arrendamiento_id: int,
    current=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    a = db.query(Arrendamiento).filter(Arrendamiento.id_arrendamiento == arrendamiento_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Arrendamiento no encontrado")
    return a


@router.post("/", response_model=ArrendamientoOut, status_code=status.HTTP_201_CREATED,
             summary="Registrar arrendamiento")
def create_arrendamiento(
    data: ArrendamientoCreate,
    current=Depends(only_admin_or_supervisor),
    db: Session = Depends(get_db)
):
    # Validaciones
    if not db.query(Contenedor).filter(Contenedor.id_contenedor == data.id_contenedor).first():
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    if not db.query(Cliente).filter(Cliente.id_cliente == data.id_cliente).first():
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Validar fechas
    if data.fecha_fin and data.fecha_inicio >= data.fecha_fin:
        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la de fin")

    if data.valor_alquiler and data.valor_alquiler <= 0:
        raise HTTPException(status_code=400, detail="El valor del alquiler debe ser mayor a 0")

    nuevo = Arrendamiento(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    broadcaster.emit("arrendamiento", {"action": "created"}, exclude_user_id=current.id_usuario)
    return nuevo


@router.put("/{arrendamiento_id}", response_model=ArrendamientoOut,
            summary="Actualizar arrendamiento")
def update_arrendamiento(
    arrendamiento_id: int,
    data: ArrendamientoUpdate,
    current=Depends(only_admin_or_supervisor),
    db: Session = Depends(get_db)
):
    a = db.query(Arrendamiento).filter(Arrendamiento.id_arrendamiento == arrendamiento_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Arrendamiento no encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(a, field, value)
    db.commit()
    db.refresh(a)
    broadcaster.emit("arrendamiento", {"action": "updated"}, exclude_user_id=current.id_usuario)
    return a


@router.delete("/{arrendamiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_arrendamiento(
    arrendamiento_id: int,
    admin=Depends(only_admin),
    db: Session = Depends(get_db)
):
    a = db.query(Arrendamiento).filter(Arrendamiento.id_arrendamiento == arrendamiento_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Arrendamiento no encontrado")
    db.delete(a)
    db.commit()
    broadcaster.emit("arrendamiento", {"action": "deleted"}, exclude_user_id=admin.id_usuario)
