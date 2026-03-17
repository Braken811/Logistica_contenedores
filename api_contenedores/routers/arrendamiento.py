from typing import List
from datetime import date, timedelta
from fastapi import APIRouter, HTTPException, Query, status

from schemas import ArrendamientoCreate, ArrendamientoUpdate, ArrendamientoOut
from data_utils import load_data, save_data, get_next_id

router = APIRouter(prefix="/arrendamientos", tags=["Arrendamientos"])


@router.get("/", response_model=List[ArrendamientoOut], summary="Listar arrendamientos")
def get_arrendamientos():
    return load_data("arrendamiento.json")


# RF09: Alertas de próximo vencimiento
@router.get("/proximos-vencer", response_model=List[ArrendamientoOut],
            summary="Arrendamientos próximos a vencer")
def get_proximos_vencer(dias: int = Query(7, ge=1, le=90, description="Días de anticipación para la alerta")):
    """
    Devuelve los arrendamientos activos cuya fecha_fin
    está dentro de los próximos `dias` días.
    """
    hoy = date.today()
    limit = hoy + timedelta(days=dias)
    arrendamientos = load_data("arrendamiento.json")
    return [a for a in arrendamientos if a.get("estado_arrendamiento") == "activo" and hoy <= date.fromisoformat(a["fecha_fin"]) <= limit]


@router.get("/{arrendamiento_id}", response_model=ArrendamientoOut)
def get_arrendamiento(arrendamiento_id: int):
    arrendamientos = load_data("arrendamiento.json")
    a = next((a for a in arrendamientos if a["id_arrendamiento"] == arrendamiento_id), None)
    if not a:
        raise HTTPException(status_code=404, detail="Arrendamiento no encontrado")
    return a


@router.post("/", response_model=ArrendamientoOut, status_code=status.HTTP_201_CREATED,
             summary="Registrar arrendamiento")
def create_arrendamiento(data: ArrendamientoCreate):
    contenedores = load_data("contenedores.json")
    if not any(c["id_contenedor"] == data.id_contenedor for c in contenedores):
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    clientes = load_data("clientes.json")
    if not any(c["id_cliente"] == data.id_cliente for c in clientes):
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    arrendamientos = load_data("arrendamiento.json")
    nuevo = data.model_dump()
    nuevo["id_arrendamiento"] = get_next_id(arrendamientos, "id_arrendamiento")
    arrendamientos.append(nuevo)
    save_data("arrendamiento.json", arrendamientos)
    return nuevo


@router.put("/{arrendamiento_id}", response_model=ArrendamientoOut,
            summary="Actualizar arrendamiento")
def update_arrendamiento(arrendamiento_id: int, data: ArrendamientoUpdate):
    arrendamientos = load_data("arrendamiento.json")
    a = next((a for a in arrendamientos if a["id_arrendamiento"] == arrendamiento_id), None)
    if not a:
        raise HTTPException(status_code=404, detail="Arrendamiento no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    a.update(update_data)
    save_data("arrendamiento.json", arrendamientos)
    return a


@router.delete("/{arrendamiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_arrendamiento(arrendamiento_id: int):
    arrendamientos = load_data("arrendamiento.json")
    a = next((a for a in arrendamientos if a["id_arrendamiento"] == arrendamiento_id), None)
    if not a:
        raise HTTPException(status_code=404, detail="Arrendamiento no encontrado")
    arrendamientos.remove(a)
    save_data("arrendamiento.json", arrendamientos)
