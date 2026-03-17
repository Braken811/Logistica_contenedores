from typing import List
from fastapi import APIRouter, HTTPException, status
from datetime import date

from schemas import FacturacionCreate, FacturacionOut
from data_utils import load_data, save_data, get_next_id

router = APIRouter(prefix="/facturacion", tags=["Facturación"])


@router.get("/", response_model=List[FacturacionOut], summary="Listar facturaciones")
def get_facturaciones():
    facturaciones = load_data("facturacion.json")
    return sorted(facturaciones, key=lambda x: x.get("fecha_facturacion", ""), reverse=True)


@router.get("/contenedor/{contenedor_id}", response_model=List[FacturacionOut],
            summary="Facturaciones de un contenedor")
def get_facturaciones_contenedor(contenedor_id: int):
    contenedores = load_data("contenedores.json")
    if not any(c["id_contenedor"] == contenedor_id for c in contenedores):
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    facturaciones = load_data("facturacion.json")
    filtered = [f for f in facturaciones if f["id_contenedor"] == contenedor_id]
    return sorted(filtered, key=lambda x: x.get("fecha_facturacion", ""))


@router.post("/", response_model=FacturacionOut, status_code=status.HTTP_201_CREATED,
             summary="Registrar facturación")
def create_facturacion(data: FacturacionCreate):
    contenedores = load_data("contenedores.json")
    if not any(c["id_contenedor"] == data.id_contenedor for c in contenedores):
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    facturaciones = load_data("facturacion.json")
    nuevo = data.model_dump()
    nuevo["id_factura"] = get_next_id(facturaciones, "id_factura")
    nuevo["fecha_facturacion"] = date.today().isoformat()
    facturaciones.append(nuevo)
    save_data("facturacion.json", facturaciones)
    return nuevo


@router.delete("/{factura_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_facturacion(factura_id: int):
    facturaciones = load_data("facturacion.json")
    f = next((f for f in facturaciones if f["id_factura"] == factura_id), None)
    if not f:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    facturaciones.remove(f)
    save_data("facturacion.json", facturaciones)
