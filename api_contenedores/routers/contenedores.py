from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date

from database import get_db
from schemas import ContenedorCreate, ContenedorUpdate, ContenedorOut, EstadoContenedor
from auth_utils import get_current_user, require_admin
import models

router = APIRouter(prefix="/contenedores", tags=["Contenedores"])


# ── RF06: Consulta y búsqueda ─────────────────────────────────────────────────
@router.get("/", response_model=List[ContenedorOut], summary="Listar / buscar contenedores")
def get_contenedores(
    codigo    : Optional[str]              = Query(None, description="Filtrar por código"),
    estado    : Optional[EstadoContenedor] = Query(None, description="Filtrar por estado"),
    id_cliente: Optional[int]              = Query(None, description="Filtrar por cliente"),
    id_tipo   : Optional[int]              = Query(None, description="Filtrar por tipo"),
    skip      : int = Query(0,   ge=0),
    limit     : int = Query(100, le=500),
    db        : Session = Depends(get_db),
    _         : models.Usuario = Depends(get_current_user)
):
    """
    Soporta filtros combinables:
    - **codigo**: búsqueda exacta o parcial por id_codigo
    - **estado**: uno de los 6 estados válidos
    - **id_cliente**: ID del cliente asociado
    - **id_tipo**: ID del tipo de contenedor
    """
    q = db.query(models.Contenedor)
    if codigo:
        q = q.filter(models.Contenedor.id_codigo.ilike(f"%{codigo}%"))
    if estado:
        q = q.filter(models.Contenedor.estado == estado.value)
    if id_cliente:
        q = q.filter(models.Contenedor.id_cliente == id_cliente)
    if id_tipo:
        q = q.filter(models.Contenedor.id_tipo == id_tipo)
    return q.offset(skip).limit(limit).all()


@router.get("/{contenedor_id}", response_model=ContenedorOut, summary="Obtener contenedor")
def get_contenedor(
    contenedor_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    c = db.query(models.Contenedor).filter(
        models.Contenedor.id_contenedor == contenedor_id
    ).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    return c


# ── RF04: Agregar contenedor ──────────────────────────────────────────────────
@router.post("/", response_model=ContenedorOut, status_code=status.HTTP_201_CREATED,
             summary="Crear contenedor")
def create_contenedor(
    data: ContenedorCreate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    if db.query(models.Contenedor).filter(
        models.Contenedor.id_codigo == data.id_codigo
    ).first():
        raise HTTPException(status_code=400, detail="El código del contenedor ya existe")

    nuevo = models.Contenedor(**data.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ── RF04: Editar contenedor ───────────────────────────────────────────────────
@router.put("/{contenedor_id}", response_model=ContenedorOut, summary="Actualizar contenedor")
def update_contenedor(
    contenedor_id: int,
    data: ContenedorUpdate,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    c = db.query(models.Contenedor).filter(
        models.Contenedor.id_contenedor == contenedor_id
    ).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(c, field, value.value if hasattr(value, "value") else value)

    c.updated_at = date.today()
    db.commit()
    db.refresh(c)
    return c


# ── RF05: Actualizar estado operativo ─────────────────────────────────────────
@router.patch("/{contenedor_id}/estado", response_model=ContenedorOut,
              summary="Actualizar estado operativo")
def update_estado(
    contenedor_id: int,
    estado: EstadoContenedor,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Actualiza el estado del contenedor y guarda el cambio en Historial_Estado.
    """
    c = db.query(models.Contenedor).filter(
        models.Contenedor.id_contenedor == contenedor_id
    ).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    # Cerrar historial anterior
    historial_activo = db.query(models.HistorialEstado).filter(
        models.HistorialEstado.id_contenedor == contenedor_id,
        models.HistorialEstado.fecha_fin == None
    ).first()
    if historial_activo:
        historial_activo.fecha_fin = date.today()

    # Nuevo registro de historial
    nuevo_historial = models.HistorialEstado(
        id_contenedor=contenedor_id,
        estado=estado.value,
        fecha_inicio=date.today()
    )
    db.add(nuevo_historial)

    c.estado     = estado.value
    c.updated_at = date.today()
    db.commit()
    db.refresh(c)
    return c


# ── RF04: Eliminar contenedor ─────────────────────────────────────────────────
@router.delete("/{contenedor_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar contenedor")
def delete_contenedor(
    contenedor_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(require_admin)
):
    c = db.query(models.Contenedor).filter(
        models.Contenedor.id_contenedor == contenedor_id
    ).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    db.delete(c)
    db.commit()


# ── RF10: Historial completo del contenedor ───────────────────────────────────
@router.get("/{contenedor_id}/historial", summary="Historial completo del contenedor")
def get_historial_contenedor(
    contenedor_id: int,
    db: Session = Depends(get_db),
    _: models.Usuario = Depends(get_current_user)
):
    """
    Devuelve en un solo endpoint:
    movimientos, cambios de estado, fotos, arrendamientos y facturaciones.
    """
    c = db.query(models.Contenedor).filter(
        models.Contenedor.id_contenedor == contenedor_id
    ).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    movimientos = db.query(models.Movimiento).filter(
        models.Movimiento.id_contenedor == contenedor_id
    ).order_by(models.Movimiento.fecha_hora).all()

    historial = db.query(models.HistorialEstado).filter(
        models.HistorialEstado.id_contenedor == contenedor_id
    ).order_by(models.HistorialEstado.fecha_inicio).all()

    fotos = db.query(models.FotoContenedor).filter(
        models.FotoContenedor.id_contenedor == contenedor_id
    ).all()

    arrendamientos = db.query(models.ArrendamientoContenedor).filter(
        models.ArrendamientoContenedor.id_contenedor == contenedor_id
    ).all()

    facturaciones = db.query(models.Facturacion).filter(
        models.Facturacion.id_contenedor == contenedor_id
    ).order_by(models.Facturacion.fecha_facturacion).all()

    return {
        "contenedor"    : c,
        "movimientos"   : movimientos,
        "historial_estado": historial,
        "fotos"         : fotos,
        "arrendamientos": arrendamientos,
        "facturaciones" : facturaciones,
    }
