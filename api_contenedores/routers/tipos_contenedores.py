from typing import List
from fastapi import APIRouter, HTTPException, status

from schemas import TipoContenedorCreate, TipoContenedorOut
from data_utils import load_data, save_data, get_next_id

router = APIRouter(prefix="/tipos-contenedores", tags=["Tipos de Contenedores"])


@router.get("/", response_model=List[TipoContenedorOut], summary="Listar tipos")
def get_tipos():
    return load_data("tipos_contenedores.json")


@router.get("/{tipo_id}", response_model=TipoContenedorOut)
def get_tipo(tipo_id: int):
    tipos = load_data("tipos_contenedores.json")
    tipo = next((t for t in tipos if t["id_tipo"] == tipo_id), None)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo no encontrado")
    return tipo


@router.post("/", response_model=TipoContenedorOut, status_code=status.HTTP_201_CREATED,
             summary="Crear tipo de contenedor")
def create_tipo(data: TipoContenedorCreate):
    tipos = load_data("tipos_contenedores.json")
    nuevo = data.model_dump()
    nuevo["id_tipo"] = get_next_id(tipos, "id_tipo")
    tipos.append(nuevo)
    save_data("tipos_contenedores.json", tipos)
    return nuevo


@router.delete("/{tipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tipo(tipo_id: int):
    tipos = load_data("tipos_contenedores.json")
    tipo = next((t for t in tipos if t["id_tipo"] == tipo_id), None)
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo no encontrado")
    tipos.remove(tipo)
    save_data("tipos_contenedores.json", tipos)
