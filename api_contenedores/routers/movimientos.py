from typing import List
from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from schemas import MovimientoCreate, MovimientoOut
from data_utils import load_data, save_data, get_next_id

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])


@router.get("/", response_model=List[MovimientoOut], summary="Listar movimientos")
def get_movimientos():
    movimientos = load_data("movimientos.json")
    return sorted(movimientos, key=lambda x: x.get("fecha_hora", ""), reverse=True)


# RF01: Movimientos de un contenedor específico
@router.get("/contenedor/{contenedor_id}", response_model=List[MovimientoOut],
            summary="Movimientos de un contenedor (cronológico)")
def get_movimientos_contenedor(contenedor_id: int):
    contenedores = load_data("contenedores.json")
    if not any(c["id_contenedor"] == contenedor_id for c in contenedores):
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    movimientos = load_data("movimientos.json")
    filtered = [m for m in movimientos if m["id_contenedor"] == contenedor_id]
    return sorted(filtered, key=lambda x: x.get("fecha_hora", ""))


@router.post("/", response_model=MovimientoOut, status_code=status.HTTP_201_CREATED,
             summary="Registrar movimiento")
def create_movimiento(data: MovimientoCreate):
    contenedores = load_data("contenedores.json")
    if not any(c["id_contenedor"] == data.id_contenedor for c in contenedores):
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    movimientos = load_data("movimientos.json")
    nuevo = data.model_dump()
    nuevo["id_movimiento"] = get_next_id(movimientos, "id_movimiento")
    nuevo["fecha_hora"] = datetime.now().isoformat()
    movimientos.append(nuevo)
    save_data("movimientos.json", movimientos)
    return nuevo


@router.delete("/{movimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movimiento(movimiento_id: int):
    movimientos = load_data("movimientos.json")
    m = next((m for m in movimientos if m["id_movimiento"] == movimiento_id), None)
    if not m:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    movimientos.remove(m)
    save_data("movimientos.json", movimientos)
