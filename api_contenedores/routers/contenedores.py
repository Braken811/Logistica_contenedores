from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status, Depends
from datetime import date
from sqlalchemy.orm import Session

from schemas import ContenedorCreate, ContenedorUpdate, ContenedorOut, EstadoContenedor
from database import get_db
from models import Contenedor, HistorialEstado, Movimiento, Foto, Arrendamiento, Facturacion
from auth.dependencies import get_current_user, only_admin

router = APIRouter(prefix="/contenedores", tags=["Contenedores"])


# ── RF06: Consulta y búsqueda ─────────────────────────────────────────────────
@router.get("/", response_model=List[ContenedorOut], summary="Listar / buscar contenedores")
def get_contenedores(current=Depends(get_current_user), 
    db: Session = Depends(get_db),
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
    query = db.query(Contenedor)
    if codigo:
        query = query.filter(Contenedor.id_codigo.ilike(f"%{codigo}%"))
    if estado:
        query = query.filter(Contenedor.estado == estado)
    if id_cliente:
        query = query.filter(Contenedor.id_cliente == id_cliente)
    if id_tipo:
        query = query.filter(Contenedor.id_tipo == id_tipo)
    return query.offset(skip).limit(limit).all()


@router.get("/{contenedor_id}", response_model=ContenedorOut, summary="Obtener contenedor")
def get_contenedor(contenedor_id: int, current=Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Contenedor).filter(Contenedor.id_contenedor == contenedor_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    return c


# ── RF04: Agregar contenedor ──────────────────────────────────────────────────
@router.post("/", response_model=ContenedorOut, status_code=status.HTTP_201_CREATED,
             summary="Crear contenedor")
def create_contenedor(data: ContenedorCreate, admin=Depends(only_admin), db: Session = Depends(get_db)):
    if db.query(Contenedor).filter(Contenedor.id_codigo == data.id_codigo).first():
        raise HTTPException(status_code=400, detail="El código del contenedor ya existe")

    nuevo = Contenedor(**data.model_dump(), created_at=date.today(), updated_at=date.today())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ── RF04: Editar contenedor ───────────────────────────────────────────────────
@router.put("/{contenedor_id}", response_model=ContenedorOut, summary="Actualizar contenedor")
def update_contenedor(contenedor_id: int, data: ContenedorUpdate, admin=Depends(only_admin), db: Session = Depends(get_db)):
    c = db.query(Contenedor).filter(Contenedor.id_contenedor == contenedor_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(c, field, value)
    c.updated_at = date.today()
    db.commit()
    db.refresh(c)
    return c


# ── RF05: Actualizar estado operativo ─────────────────────────────────────────
@router.patch("/{contenedor_id}/estado", response_model=ContenedorOut,
              summary="Actualizar estado operativo")
def update_estado(contenedor_id: int, estado: EstadoContenedor, admin=Depends(only_admin), db: Session = Depends(get_db)):
    """
    Actualiza el estado del contenedor y guarda el cambio en Historial_Estado.
    """
    c = db.query(Contenedor).filter(Contenedor.id_contenedor == contenedor_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    # Cerrar historial anterior
    activo = db.query(HistorialEstado).filter(HistorialEstado.id_contenedor == contenedor_id, HistorialEstado.fecha_fin.is_(None)).first()
    if activo:
        activo.fecha_fin = date.today()

    # Nuevo registro de historial
    nuevo_historial = HistorialEstado(id_contenedor=contenedor_id, estado=estado, fecha_inicio=date.today())
    db.add(nuevo_historial)

    c.estado = estado
    c.updated_at = date.today()
    db.commit()
    db.refresh(c)
    return c


# ── RF04: Eliminar contenedor ─────────────────────────────────────────────────
@router.delete("/{contenedor_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar contenedor")
def delete_contenedor(contenedor_id: int, db: Session = Depends(get_db)):
    c = db.query(Contenedor).filter(Contenedor.id_contenedor == contenedor_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    db.delete(c)
    db.commit()


# ── RF10: Historial completo del contenedor ───────────────────────────────────
@router.get("/{contenedor_id}/historial", summary="Historial completo del contenedor")
def get_historial_contenedor(contenedor_id: int, db: Session = Depends(get_db)):
    """
    Devuelve en un solo endpoint:
    movimientos, cambios de estado, fotos, arrendamientos y facturaciones.
    """
    c = db.query(Contenedor).filter(Contenedor.id_contenedor == contenedor_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    movimientos = db.query(Movimiento).filter(Movimiento.id_contenedor == contenedor_id).order_by(Movimiento.fecha_hora).all()
    historial_estado = db.query(HistorialEstado).filter(HistorialEstado.id_contenedor == contenedor_id).order_by(HistorialEstado.fecha_inicio).all()
    fotos = db.query(Foto).filter(Foto.id_contenedor == contenedor_id).all()
    arrendamientos = db.query(Arrendamiento).filter(Arrendamiento.id_contenedor == contenedor_id).all()
    facturaciones = db.query(Facturacion).filter(Facturacion.id_contenedor == contenedor_id).order_by(Facturacion.fecha_facturacion).all()

    return {
        "contenedor"    : c,
        "movimientos"   : movimientos,
        "historial_estado": historial_estado,
        "fotos"         : fotos,
        "arrendamientos": arrendamientos,
        "facturaciones" : facturaciones,
    }
