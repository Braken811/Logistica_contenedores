from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas import ClienteCreate, ClienteUpdate, ClienteOut
from auth_utils import get_current_user, require_admin
import models

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/", response_model=List[ClienteOut], summary="Listar clientes")
def get_clientes(
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    return db.query(models.Cliente).all()


@router.get("/{cliente_id}", response_model=ClienteOut, summary="Obtener cliente por ID")
def get_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    cliente = db.query(models.Cliente).filter(models.Cliente.id_cliente == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.post("/", response_model=ClienteOut, status_code=status.HTTP_201_CREATED,
             summary="Crear cliente")
def create_cliente(
    data: ClienteCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    if db.query(models.Cliente).filter(models.Cliente.nit == data.nit).first():
        raise HTTPException(status_code=400, detail="Ya existe un cliente con ese NIT")

    nuevo = models.Cliente(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{cliente_id}", response_model=ClienteOut, summary="Actualizar cliente")
def update_cliente(
    cliente_id: int,
    data: ClienteUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    cliente = db.query(models.Cliente).filter(models.Cliente.id_cliente == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cliente, field, value)

    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar cliente")
def delete_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    cliente = db.query(models.Cliente).filter(models.Cliente.id_cliente == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(cliente)
    db.commit()
