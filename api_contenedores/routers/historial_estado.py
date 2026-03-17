# routers/historial_estado.py
from typing import List
from fastapi import APIRouter, HTTPException, status

from schemas import HistorialEstadoCreate, HistorialEstadoOut
from data_utils import load_data, save_data, get_next_id

router = APIRouter(prefix="/historial-estado", tags=["Historial de Estado"])


@router.get("/contenedor/{contenedor_id}", response_model=List[HistorialEstadoOut])
def get_historial(contenedor_id: int):
    contenedores = load_data("contenedores.json")
    if not any(c["id_contenedor"] == contenedor_id for c in contenedores):
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    historial = load_data("historial_estado.json")
    filtered = [h for h in historial if h["id_contenedor"] == contenedor_id]
    return sorted(filtered, key=lambda x: x["fecha_inicio"])


@router.post("/", response_model=HistorialEstadoOut, status_code=status.HTTP_201_CREATED)
def create_historial(data: HistorialEstadoCreate):
    contenedores = load_data("contenedores.json")
    if not any(c["id_contenedor"] == data.id_contenedor for c in contenedores):
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    historial = load_data("historial_estado.json")
    nuevo = data.model_dump()
    nuevo["id_historial"] = get_next_id(historial, "id_historial")
    nuevo["estado"] = data.estado.value
    historial.append(nuevo)
    save_data("historial_estado.json", historial)
    return nuevo
