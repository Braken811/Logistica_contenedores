from typing import List
from fastapi import APIRouter, HTTPException, status

from schemas import ClienteCreate, ClienteUpdate, ClienteOut
from data_utils import load_data, save_data, get_next_id

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/", response_model=List[ClienteOut], summary="Listar clientes")
def get_clientes():
    return load_data("clientes.json")


@router.get("/{cliente_id}", response_model=ClienteOut, summary="Obtener cliente por ID")
def get_cliente(cliente_id: int):
    clientes = load_data("clientes.json")
    cliente = next((c for c in clientes if c["id_cliente"] == cliente_id), None)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@router.post("/", response_model=ClienteOut, status_code=status.HTTP_201_CREATED,
             summary="Crear cliente")
def create_cliente(data: ClienteCreate):
    clientes = load_data("clientes.json")
    if any(c["nit"] == data.nit for c in clientes):
        raise HTTPException(status_code=400, detail="Ya existe un cliente con ese NIT")

    nuevo = data.model_dump()
    nuevo["id_cliente"] = get_next_id(clientes, "id_cliente")
    clientes.append(nuevo)
    save_data("clientes.json", clientes)
    return nuevo


@router.put("/{cliente_id}", response_model=ClienteOut, summary="Actualizar cliente")
def update_cliente(cliente_id: int, data: ClienteUpdate):
    clientes = load_data("clientes.json")
    cliente = next((c for c in clientes if c["id_cliente"] == cliente_id), None)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    cliente.update(update_data)
    save_data("clientes.json", clientes)
    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar cliente")
def delete_cliente(cliente_id: int):
    clientes = load_data("clientes.json")
    cliente = next((c for c in clientes if c["id_cliente"] == cliente_id), None)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    clientes.remove(cliente)
    save_data("clientes.json", clientes)
