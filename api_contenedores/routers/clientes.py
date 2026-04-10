from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from schemas import ClienteCreate, ClienteUpdate, ClienteOut
from database import get_db
from models import Cliente
from auth.dependencies import get_current_user, only_admin

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/", response_model=List[ClienteOut], summary="Listar clientes")
def get_clientes(current=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Cliente).all()


@router.get("/{cliente_id}", response_model=ClienteOut, summary="Obtener cliente por ID")
def get_cliente(cliente_id: int, current=Depends(get_current_user), db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id_cliente == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.post("/", response_model=ClienteOut, status_code=status.HTTP_201_CREATED,
             summary="Crear cliente")
def create_cliente(data: ClienteCreate, admin=Depends(only_admin), db: Session = Depends(get_db)):
    if db.query(Cliente).filter(Cliente.nit == data.nit).first():
        raise HTTPException(status_code=400, detail="Ya existe un cliente con ese NIT")

    nuevo = Cliente(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{cliente_id}", response_model=ClienteOut, summary="Actualizar cliente")
def update_cliente(cliente_id: int, data: ClienteUpdate, admin=Depends(only_admin), db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id_cliente == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cliente, field, value)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar cliente")
def delete_cliente(cliente_id: int, admin=Depends(only_admin), db: Session = Depends(get_db)):
    clientes = load_data("clientes.json")
    cliente = next((c for c in clientes if c["id_cliente"] == cliente_id), None)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    clientes.remove(cliente)
    save_data("clientes.json", clientes)
