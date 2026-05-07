import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status, Depends, UploadFile, File
from datetime import date, datetime
from sqlalchemy.orm import Session

from schemas import ContenedorCreate, ContenedorUpdate, ContenedorOut, EstadoContenedor
from database import get_db
from models import Contenedor, HistorialEstado, Movimiento, Foto, Arrendamiento, Facturacion
from auth.dependencies import get_current_user, only_admin, only_admin_or_supervisor, only_staff

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
def create_contenedor(data: ContenedorCreate, current=Depends(only_admin_or_supervisor), db: Session = Depends(get_db)):
    if db.query(Contenedor).filter(Contenedor.id_codigo == data.id_codigo).first():
        raise HTTPException(status_code=400, detail="El código del contenedor ya existe")

    nuevo = Contenedor(**data.model_dump(), created_at=date.today(), updated_at=date.today())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ── RF04: Editar contenedor ───────────────────────────────────────────────────
@router.put("/{contenedor_id}", response_model=ContenedorOut, summary="Actualizar contenedor")
def update_contenedor(contenedor_id: int, data: ContenedorUpdate, current=Depends(only_admin_or_supervisor), db: Session = Depends(get_db)):
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
def update_estado(contenedor_id: int, estado: EstadoContenedor, _=Depends(only_staff), db: Session = Depends(get_db)):
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
def delete_contenedor(contenedor_id: int, admin=Depends(only_admin), db: Session = Depends(get_db)):
    c = db.query(Contenedor).filter(Contenedor.id_contenedor == contenedor_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    db.delete(c)
    db.commit()


CONT_IMG_DIR = "uploads/contenedores"
os.makedirs(CONT_IMG_DIR, exist_ok=True)
_ALLOWED_IMG = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


@router.post("/{contenedor_id}/imagen", summary="Subir imagen principal del contenedor")
def upload_contenedor_imagen(
    contenedor_id: int,
    file: UploadFile = File(...),
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    c = db.query(Contenedor).filter(Contenedor.id_contenedor == contenedor_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in _ALLOWED_IMG:
        raise HTTPException(status_code=400, detail="Formato no válido. Use JPG, PNG, GIF o WEBP.")
    filename = f"cont_{contenedor_id}_{int(datetime.utcnow().timestamp())}{ext}"
    filepath = os.path.join(CONT_IMG_DIR, filename)
    with open(filepath, "wb") as buf:
        shutil.copyfileobj(file.file, buf)
    url = f"/uploads/contenedores/{filename}"
    c.ruta_imagen = url
    c.updated_at = date.today()
    db.commit()
    return {"url": url}


# ── RF10: Historial completo del contenedor ───────────────────────────────────
@router.get("/{contenedor_id}/historial", summary="Historial completo del contenedor")
def get_historial_contenedor(contenedor_id: int, current=Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Devuelve en un solo endpoint (serialización explícita):
    movimientos, cambios de estado, arrendamientos y facturaciones.
    """
    from models import Cliente

    c = db.query(Contenedor).filter(Contenedor.id_contenedor == contenedor_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contenedor no encontrado")

    movimientos      = db.query(Movimiento).filter(Movimiento.id_contenedor == contenedor_id).order_by(Movimiento.fecha_hora.desc()).all()
    historial_estado = db.query(HistorialEstado).filter(HistorialEstado.id_contenedor == contenedor_id).order_by(HistorialEstado.fecha_inicio.desc()).all()
    arrendamientos   = db.query(Arrendamiento).filter(Arrendamiento.id_contenedor == contenedor_id).order_by(Arrendamiento.fecha_inicio.desc()).all()
    facturaciones    = db.query(Facturacion).filter(Facturacion.id_contenedor == contenedor_id).order_by(Facturacion.fecha_facturacion.desc()).all()

    # Mapa cliente_id → nombre para enriquecer arrendamientos
    client_ids = {a.id_cliente for a in arrendamientos}
    clients    = {}
    if client_ids:
        for cl in db.query(Cliente).filter(Cliente.id_cliente.in_(client_ids)).all():
            clients[cl.id_cliente] = cl.nombre

    estado_val = c.estado.value if hasattr(c.estado, "value") else str(c.estado)

    return {
        "contenedor": {
            "id_contenedor"  : c.id_contenedor,
            "id_codigo"      : c.id_codigo,
            "estado"         : estado_val,
            "ubicacion_actual": c.ubicacion_actual,
        },
        "movimientos": [
            {
                "id_movimiento"    : m.id_movimiento,
                "fecha_hora"       : m.fecha_hora.isoformat() if m.fecha_hora else None,
                "fecha_salida"     : str(m.fecha_salida) if m.fecha_salida else None,
                "ubicacion_origen" : m.ubicacion_origen,
                "ubicacion_destino": m.ubicacion_destino,
                "medio_transporte" : m.medio_transporte,
                "responsable"      : m.responsable,
                "id_usuario"       : m.id_usuario,
            }
            for m in movimientos
        ],
        "historial_estado": [
            {
                "id_historial": h.id_historial,
                "estado"      : h.estado.value if hasattr(h.estado, "value") else str(h.estado),
                "fecha_inicio": str(h.fecha_inicio),
                "fecha_fin"   : str(h.fecha_fin) if h.fecha_fin else None,
            }
            for h in historial_estado
        ],
        "arrendamientos": [
            {
                "id_arrendamiento"   : a.id_arrendamiento,
                "id_cliente"         : a.id_cliente,
                "nombre_cliente"     : clients.get(a.id_cliente, f"Cliente #{a.id_cliente}"),
                "fecha_inicio"       : str(a.fecha_inicio),
                "fecha_fin"          : str(a.fecha_fin) if a.fecha_fin else None,
                "valor_alquiler"     : a.valor_alquiler,
                "estado_arrendamiento": a.estado_arrendamiento,
            }
            for a in arrendamientos
        ],
        "facturaciones": [
            {
                "id_factura"       : f.id_factura,
                "codigo_factura"   : f.codigo_factura,
                "fecha_facturacion": str(f.fecha_facturacion) if f.fecha_facturacion else None,
                "fecha_vencimiento": str(f.fecha_vencimiento) if f.fecha_vencimiento else None,
                "monto"            : f.monto,
                "estado_pago"      : f.estado_pago,
            }
            for f in facturaciones
        ],
    }


# ─── Mapa: agrupación por ciudad colombiana ───────────────────────────────────
CIUDADES_COORDS = {
    "cartagena":         {"lat": 10.3910, "lng": -75.4794, "nombre": "Cartagena"},
    "puerto cartagena":  {"lat": 10.3910, "lng": -75.4794, "nombre": "Cartagena"},
    "bogotá":            {"lat":  4.7110, "lng": -74.0721, "nombre": "Bogotá"},
    "bogota":            {"lat":  4.7110, "lng": -74.0721, "nombre": "Bogotá"},
    "medellín":          {"lat":  6.2518, "lng": -75.5636, "nombre": "Medellín"},
    "medellin":          {"lat":  6.2518, "lng": -75.5636, "nombre": "Medellín"},
    "barranquilla":      {"lat": 10.9639, "lng": -74.7964, "nombre": "Barranquilla"},
    "bucaramanga":       {"lat":  7.1193, "lng": -73.1227, "nombre": "Bucaramanga"},
    "cali":              {"lat":  3.4516, "lng": -76.5320, "nombre": "Cali"},
    "santa marta":       {"lat": 11.2408, "lng": -74.1990, "nombre": "Santa Marta"},
    "manizales":         {"lat":  5.0703, "lng": -75.5138, "nombre": "Manizales"},
    "pereira":           {"lat":  4.8133, "lng": -75.6961, "nombre": "Pereira"},
    "taller":            {"lat":  6.2442, "lng": -75.5812, "nombre": "Taller/Mantenimiento"},
    "mantenimiento":     {"lat":  6.2442, "lng": -75.5812, "nombre": "Taller/Mantenimiento"},
}

@router.get("/por-ciudad", summary="Contenedores agrupados por ciudad colombiana")
def get_contenedores_por_ciudad(current=Depends(get_current_user), db: Session = Depends(get_db)):
    contenedores = db.query(Contenedor).all()
    grupos: dict = {}
    sin_ubicacion = []

    for c in contenedores:
        ubicacion = (c.ubicacion_actual or "").lower().strip()
        ciudad_key = None
        for key in CIUDADES_COORDS:
            if key in ubicacion:
                ciudad_key = key
                break

        if ciudad_key:
            info   = CIUDADES_COORDS[ciudad_key]
            nombre = info["nombre"]
            if nombre not in grupos:
                grupos[nombre] = {
                    "nombre": nombre, "lat": info["lat"], "lng": info["lng"],
                    "total": 0, "disponibles": 0, "en_transito": 0, "contenedores": []
                }
            estado_val = c.estado.value if hasattr(c.estado, "value") else str(c.estado)
            grupos[nombre]["total"] += 1
            if estado_val == "disponible":  grupos[nombre]["disponibles"] += 1
            if estado_val == "en_transito": grupos[nombre]["en_transito"] += 1
            grupos[nombre]["contenedores"].append({
                "id_contenedor":  c.id_contenedor,
                "id_codigo":      c.id_codigo,
                "estado":         estado_val,
                "ubicacion_actual": c.ubicacion_actual,
            })
        else:
            sin_ubicacion.append({
                "id_codigo":      c.id_codigo,
                "estado":         c.estado.value if hasattr(c.estado, "value") else str(c.estado),
                "ubicacion_actual": c.ubicacion_actual,
            })

    return {
        "ciudades":     list(grupos.values()),
        "sin_ubicacion": sin_ubicacion,
        "total":        len(contenedores),
    }
