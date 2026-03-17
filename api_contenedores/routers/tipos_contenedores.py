from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import TipoContenedorCreate, TipoContenedorOut
from auth_utils import get_current_user, require_admin
import models

router = APIRouter(prefix="/tipos-contenedores", tags=["Tipos de Contenedores"])


@router.get("/", response_model=List[TipoContenedorOut], summary="Listar tipos")
def get_tipos(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    return db.query(models.TipoContenedor).all()


@router.get("/{tipo_id}", response_model=TipoContenedorOut)
def get_tipo(
    tipo_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    tipo = db.query(models.TipoContenedor).filter(models.TipoContenedor.id_tipo == tipo_id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo no encontrado")
    return tipo


@router.post("/", response_model=TipoContenedorOut, status_code=status.HTTP_201_CREATED,
             summary="Crear tipo de contenedor")
def create_tipo(
    data: TipoContenedorCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    nuevo = models.TipoContenedor(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.delete("/{tipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tipo(
    tipo_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    tipo = db.query(models.TipoContenedor).filter(models.TipoContenedor.id_tipo == tipo_id).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo no encontrado")
    db.delete(tipo)
    db.commit()
