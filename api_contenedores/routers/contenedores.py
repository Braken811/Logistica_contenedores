from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from datetime import date

from schemas import ContenedorCreate, ContenedorUpdate, ContenedorOut, EstadoContenedor
from data_utils import load_data, save_data, get_next_id

router = APIRouter(prefix="/contenedores", tags=["Contenedores"])


# ── RF06: Consulta y búsqueda ─────────────────────────────────────────────────
@router.get("/", response_model=List[ContenedorOut], summary="Listar / buscar contenedores")
def get_contenedores(
    codigo    : Optional[str]              = Query(None, description="Filtrar por código"),
    estado    : Optional[EstadoContenedor] = Query(None, description="Filtrar por estado"),
    id_cliente: Optional[int]              = Query(None, description="Filtrar por cliente"),
    id_tipo   : Optional[int]              = Query(None, description="Filtrar por tipo"),
    skip      : int = Query(0,   ge=0),
    limit     : int = Query(100, le=500)
):
    """
    Soporta filtros combinables:
    - **codigo**: búsqueda exacta o parcial por id_codigo
    - **estado**: uno de los 6 estados válidos
    - **id_cliente**: ID del cliente asociado
    - **id_tipo**: ID del tipo de contenedor
    """
    contenedores = load_data("contenedores.json")
    filtered = contenedores
    if codigo:
        filtered = [c for c in filtered if codigo.lower() in c["id_codigo"].lower()]
    if estado:
        filtered = [c for c in filtered if c["estado"] == estado.value]
    if id_cliente:
        filtered = [c for c in filtered if c["id_cliente"] == id_cliente]
    if id_tipo:
        filtered = [c for c in filtered if c["id_tipo"] == id_tipo]
    return filtered[skip:skip+limit]


@router.get("/{contenedor_id}", response_model=ContenedorOut, summary="Obtener contenedor")
def get_contenedor(contenedor_id: int):
    contenedores = load_data("contenedores.json")
    c = next((c for c in contenedores if c["id_contenedor"] == contenedor_id), None)
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    return c


# ── RF04: Agregar contenedor ──────────────────────────────────────────────────
@router.post("/", response_model=ContenedorOut, status_code=status.HTTP_201_CREATED,
             summary="Crear contenedor")
def create_contenedor(data: ContenedorCreate):
    contenedores = load_data("contenedores.json")
    if any(c["id_codigo"] == data.id_codigo for c in contenedores):
        raise HTTPException(status_code=400, detail="El código del contenedor ya existe")

    nuevo = data.model_dump()
    nuevo["id_contenedor"] = get_next_id(contenedores, "id_contenedor")
    nuevo["created_at"] = date.today().isoformat()
    nuevo["updated_at"] = date.today().isoformat()
    contenedores.append(nuevo)
    save_data("contenedores.json", contenedores)
    return nuevo


# ── RF04: Editar contenedor ───────────────────────────────────────────────────
@router.put("/{contenedor_id}", response_model=ContenedorOut, summary="Actualizar contenedor")
def update_contenedor(contenedor_id: int, data: ContenedorUpdate):
    contenedores = load_data("contenedores.json")
    c = next((c for c in contenedores if c["id_contenedor"] == contenedor_id), None)
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(value, "value"):
            c[field] = value.value
        else:
            c[field] = value
    c["updated_at"] = date.today().isoformat()
    save_data("contenedores.json", contenedores)
    return c


# ── RF05: Actualizar estado operativo ─────────────────────────────────────────
@router.patch("/{contenedor_id}/estado", response_model=ContenedorOut,
              summary="Actualizar estado operativo")
def update_estado(contenedor_id: int, estado: EstadoContenedor):
    """
    Actualiza el estado del contenedor y guarda el cambio en Historial_Estado.
    """
    contenedores = load_data("contenedores.json")
    c = next((c for c in contenedores if c["id_contenedor"] == contenedor_id), None)
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    # Cerrar historial anterior
    historial = load_data("historial_estado.json")
    activo = next((h for h in historial if h["id_contenedor"] == contenedor_id and h.get("fecha_fin") is None), None)
    if activo:
        activo["fecha_fin"] = date.today().isoformat()

    # Nuevo registro de historial
    nuevo_historial = {
        "id_historial": get_next_id(historial, "id_historial"),
        "id_contenedor": contenedor_id,
        "estado": estado.value,
        "fecha_inicio": date.today().isoformat(),
        "fecha_fin": None
    }
    historial.append(nuevo_historial)
    save_data("historial_estado.json", historial)

    c["estado"] = estado.value
    c["updated_at"] = date.today().isoformat()
    save_data("contenedores.json", contenedores)
    return c


# ── RF04: Eliminar contenedor ─────────────────────────────────────────────────
@router.delete("/{contenedor_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar contenedor")
def delete_contenedor(contenedor_id: int):
    contenedores = load_data("contenedores.json")
    c = next((c for c in contenedores if c["id_contenedor"] == contenedor_id), None)
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    contenedores.remove(c)
    save_data("contenedores.json", contenedores)


# ── RF10: Historial completo del contenedor ───────────────────────────────────
@router.get("/{contenedor_id}/historial", summary="Historial completo del contenedor")
def get_historial_contenedor(contenedor_id: int):
    """
    Devuelve en un solo endpoint:
    movimientos, cambios de estado, fotos, arrendamientos y facturaciones.
    """
    contenedores = load_data("contenedores.json")
    c = next((c for c in contenedores if c["id_contenedor"] == contenedor_id), None)
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    movimientos = load_data("movimientos.json")
    movimientos_filtered = [m for m in movimientos if m["id_contenedor"] == contenedor_id]
    movimientos_filtered.sort(key=lambda x: x.get("fecha_hora", ""))

    historial = load_data("historial_estado.json")
    historial_filtered = [h for h in historial if h["id_contenedor"] == contenedor_id]
    historial_filtered.sort(key=lambda x: x["fecha_inicio"])

    fotos = load_data("fotos.json")
    fotos_filtered = [f for f in fotos if f["id_contenedor"] == contenedor_id]

    arrendamientos = load_data("arrendamiento.json")
    arrendamientos_filtered = [a for a in arrendamientos if a["id_contenedor"] == contenedor_id]

    facturaciones = load_data("facturacion.json")
    facturaciones_filtered = [f for f in facturaciones if f["id_contenedor"] == contenedor_id]
    facturaciones_filtered.sort(key=lambda x: x.get("fecha_facturacion", ""))

    return {
        "contenedor"    : c,
        "movimientos"   : movimientos_filtered,
        "historial_estado": historial_filtered,
        "fotos"         : fotos_filtered,
        "arrendamientos": arrendamientos_filtered,
        "facturaciones" : facturaciones_filtered,
    }
