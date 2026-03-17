from typing import List
from fastapi import APIRouter, HTTPException, status
from datetime import date

from schemas import VentaCreate, VentaOut
from data_utils import load_data, save_data, get_next_id

router = APIRouter(prefix="/ventas", tags=["Ventas"])


@router.get("/", response_model=List[VentaOut], summary="Listar ventas")
def get_ventas():
    ventas = load_data("ventas.json")
    return sorted(ventas, key=lambda x: x.get("fecha_venta", ""), reverse=True)


@router.get("/{venta_id}", response_model=VentaOut)
def get_venta(venta_id: int):
    ventas = load_data("ventas.json")
    v = next((v for v in ventas if v["id_venta"] == venta_id), None)
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return v


@router.post("/", response_model=VentaOut, status_code=status.HTTP_201_CREATED,
             summary="Registrar venta")
def create_venta(data: VentaCreate):
    contenedores = load_data("contenedores.json")
    if not any(c["id_contenedor"] == data.id_contenedor for c in contenedores):
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    clientes = load_data("clientes.json")
    if not any(c["id_cliente"] == data.id_cliente for c in clientes):
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    ventas = load_data("ventas.json")
    nuevo = data.model_dump()
    nuevo["id_venta"] = get_next_id(ventas, "id_venta")
    nuevo["fecha_venta"] = date.today().isoformat()
    ventas.append(nuevo)
    save_data("ventas.json", ventas)
    return nuevo


@router.delete("/{venta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_venta(venta_id: int):
    ventas = load_data("ventas.json")
    v = next((v for v in ventas if v["id_venta"] == venta_id), None)
    if not v:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    ventas.remove(v)
    save_data("ventas.json", ventas)
