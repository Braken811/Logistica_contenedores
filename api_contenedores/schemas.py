"""
Schemas Pydantic — validación de entrada/salida.
Proyecto: Talento Tech 2026
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


# ── Enums ─────────────────────────────────────────────────────────────────────
class EstadoContenedor(str, Enum):
    disponible        = "disponible"
    asignado          = "asignado"
    en_transito       = "en_transito"
    en_patio          = "en_patio"
    en_mantenimiento  = "en_mantenimiento"
    fuera_de_servicio = "fuera_de_servicio"

class RolUsuario(str, Enum):
    admin      = "admin"
    supervisor = "supervisor"
    operador   = "operador"
    auditor    = "auditor"


# ── Usuarios ──────────────────────────────────────────────────────────────────
class UsuarioCreate(BaseModel):
    nombres         : str
    apellidos       : Optional[str] = None
    email           : Optional[str] = None
    user            : str
    password        : str
    rol             : RolUsuario

class UsuarioUpdate(BaseModel):
    nombres         : Optional[str]      = None
    apellidos       : Optional[str]      = None
    email           : Optional[str]      = None
    rol             : Optional[RolUsuario] = None
    password        : Optional[str]      = None
    email_verificado: Optional[bool]     = None

class UsuarioOut(BaseModel):
    id_usuario      : int
    nombres         : str
    apellidos       : Optional[str]
    email           : Optional[str]
    user            : str
    rol             : str
    email_verificado: bool = False

    class Config:
        from_attributes = True


# ── Clientes ──────────────────────────────────────────────────────────────────
class ClienteCreate(BaseModel):
    nombre   : str
    nit      : str
    telefono : Optional[str] = None
    email    : Optional[str] = None
    direccion: Optional[str] = None

class ClienteUpdate(BaseModel):
    nombre   : Optional[str] = None
    telefono : Optional[str] = None
    email    : Optional[str] = None
    direccion: Optional[str] = None

class ClienteOut(BaseModel):
    id_cliente: int
    nombre    : str
    nit       : str
    telefono  : Optional[str]
    email     : Optional[str]
    direccion : Optional[str]

    class Config:
        from_attributes = True


# ── Tipos de Contenedores ─────────────────────────────────────────────────────
class TipoContenedorCreate(BaseModel):
    nombre     : str
    descripcion: Optional[str] = None

class TipoContenedorOut(BaseModel):
    id_tipo    : int
    nombre     : str
    descripcion: Optional[str]

    class Config:
        from_attributes = True


# ── Contenedores ──────────────────────────────────────────────────────────────
class ContenedorCreate(BaseModel):
    id_codigo       : str
    id_tipo         : int
    id_cliente      : Optional[int]           = None
    estado          : EstadoContenedor        = EstadoContenedor.disponible
    ubicacion_actual: Optional[str]           = None
    ruta_imagen     : Optional[str]           = None

class ContenedorUpdate(BaseModel):
    id_tipo         : Optional[int]              = None
    id_cliente      : Optional[int]              = None
    estado          : Optional[EstadoContenedor] = None
    ubicacion_actual: Optional[str]              = None
    ruta_imagen     : Optional[str]              = None

class ContenedorOut(BaseModel):
    id_contenedor   : int
    id_codigo       : str
    id_tipo         : int
    id_cliente      : Optional[int]
    estado          : str
    ubicacion_actual: Optional[str]
    ruta_imagen     : Optional[str]
    created_at      : Optional[date]
    updated_at      : Optional[date]

    class Config:
        from_attributes = True


# ── Movimientos ───────────────────────────────────────────────────────────────
class MovimientoCreate(BaseModel):
    id_contenedor    : int
    id_usuario       : int
    ubicacion_origen : Optional[str] = None
    ubicacion_destino: Optional[str] = None
    medio_transporte : Optional[str] = None
    responsable      : Optional[str] = None

class MovimientoOut(BaseModel):
    id_movimiento    : int
    id_contenedor    : int
    id_usuario       : int
    fecha_hora       : Optional[datetime]
    ubicacion_origen : Optional[str]
    ubicacion_destino: Optional[str]
    medio_transporte : Optional[str]
    responsable      : Optional[str]

    class Config:
        from_attributes = True


# ── Historial de Estado ───────────────────────────────────────────────────────
class HistorialEstadoCreate(BaseModel):
    id_contenedor: int
    estado       : EstadoContenedor
    fecha_inicio : date
    fecha_fin    : Optional[date] = None

class HistorialEstadoOut(BaseModel):
    id_historial : int
    id_contenedor: int
    estado       : str
    fecha_inicio : date
    fecha_fin    : Optional[date]

    class Config:
        from_attributes = True


# ── Fotos ─────────────────────────────────────────────────────────────────────
class FotoCreate(BaseModel):
    id_contenedor: int
    ruta_imagen  : str

class FotoOut(BaseModel):
    id_foto      : int
    id_contenedor: int
    ruta_imagen  : str
    fecha_subida : Optional[date]

    class Config:
        from_attributes = True


# ── Arrendamiento ─────────────────────────────────────────────────────────────
class ArrendamientoCreate(BaseModel):
    id_cliente          : int
    id_contenedor       : int
    fecha_inicio        : date
    fecha_fin           : Optional[date] = None
    valor_alquiler      : float
    estado_arrendamiento: str = "activo"

class ArrendamientoUpdate(BaseModel):
    fecha_fin           : Optional[date]  = None
    valor_alquiler      : Optional[float] = None
    estado_arrendamiento: Optional[str]   = None

class ArrendamientoOut(BaseModel):
    id_arrendamiento    : int
    id_cliente          : int
    id_contenedor       : int
    fecha_inicio        : date
    fecha_fin           : Optional[date]
    valor_alquiler      : float
    estado_arrendamiento: str

    class Config:
        from_attributes = True


# ── Facturación ───────────────────────────────────────────────────────────────
class FacturacionCreate(BaseModel):
    id_contenedor     : int
    monto             : float
    observaciones     : Optional[str]  = None
    codigo_factura    : Optional[str]  = None
    fecha_vencimiento : Optional[date] = None
    estado_pago       : str            = "pendiente"

class FacturacionUpdate(BaseModel):
    monto             : Optional[float] = None
    observaciones     : Optional[str]   = None
    estado_pago       : Optional[str]   = None
    fecha_vencimiento : Optional[date]  = None

class FacturacionOut(BaseModel):
    id_factura        : int
    id_contenedor     : int
    fecha_facturacion : Optional[date]
    monto             : float
    observaciones     : Optional[str]
    codigo_factura    : Optional[str]
    fecha_vencimiento : Optional[date]
    estado_pago       : str

    class Config:
        from_attributes = True


# ── Ventas ────────────────────────────────────────────────────────────────────
class VentaCreate(BaseModel):
    id_contenedor: int
    id_cliente   : int
    precio       : float

class VentaOut(BaseModel):
    id_venta     : int
    id_contenedor: int
    id_cliente   : int
    fecha_venta  : Optional[date]
    precio       : float

    class Config:
        from_attributes = True


# ── Dashboard ─────────────────────────────────────────────────────────────────
class DashboardStats(BaseModel):
    total_contenedores     : int
    por_estado             : dict
    por_tipo               : dict
    por_cliente            : dict
    arrendamientos_activos : int
    proximos_vencer        : int
    total_movimientos      : int

class NotificacionItem(BaseModel):
    tipo   : str
    titulo : str
    mensaje: str
    fecha  : str
    leido  : bool = False


# ── Autenticación ─────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    user    : str
    password: str

class Token(BaseModel):
    access_token: str
    token_type  : str = "bearer"
    role        : str

class TokenData(BaseModel):
    user: Optional[str] = None
    role: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type  : str = "bearer"
    rol         : str
    nombres     : str
