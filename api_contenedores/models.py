"""
Modelos ORM — mapeados 1:1 con las tablas del script SQL.
Motor: SQL Server  |  Proyecto: Talento Tech 2026
"""
from datetime import date, datetime
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime,
    LargeBinary, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from database import Base


# ── Usuarios ──────────────────────────────────────────────────────────────────
class Usuario(Base):
    __tablename__ = "Usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombres    = Column(String(50),  nullable=False)
    apellidos  = Column(String(70))
    email      = Column(String(250), unique=True)
    user       = Column("user", String(50), unique=True, nullable=False)
    password   = Column(LargeBinary(256), nullable=False)
    rol        = Column(String(20),  nullable=False)

    movimientos = relationship("Movimiento", back_populates="usuario")


# ── Clientes ──────────────────────────────────────────────────────────────────
class Cliente(Base):
    __tablename__ = "Clientes"

    id_cliente = Column(Integer, primary_key=True, index=True)
    nombre     = Column(String(100), nullable=False)
    nit        = Column(String(20),  unique=True, nullable=False)
    telefono   = Column(String(10))
    email      = Column(String(250))
    direccion  = Column(String(250))

    contenedores   = relationship("Contenedor",           back_populates="cliente")
    arrendamientos = relationship("ArrendamientoContenedor", back_populates="cliente")
    ventas         = relationship("VentaContenedor",      back_populates="cliente")


# ── Tipos de Contenedores ─────────────────────────────────────────────────────
class TipoContenedor(Base):
    __tablename__ = "Tipos_Contenedores"

    id_tipo     = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String(50),  nullable=False)
    descripcion = Column(String(100))

    contenedores = relationship("Contenedor", back_populates="tipo")


# ── Contenedores ──────────────────────────────────────────────────────────────
ESTADOS_VALIDOS = (
    "disponible", "asignado", "en_transito",
    "en_patio", "en_mantenimiento", "fuera_de_servicio"
)

class Contenedor(Base):
    __tablename__ = "Contenedores"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('disponible','asignado','en_transito',"
            "'en_patio','en_mantenimiento','fuera_de_servicio')",
            name="CHK_Estado_Contenedor"
        ),
    )

    id_contenedor    = Column(Integer, primary_key=True, index=True)
    id_codigo        = Column(String(20),  unique=True, nullable=False)
    id_tipo          = Column(Integer, ForeignKey("Tipos_Contenedores.id_tipo"), nullable=False)
    id_cliente       = Column(Integer, ForeignKey("Clientes.id_cliente"),        nullable=False)
    estado           = Column(String(50),  nullable=False, default="disponible")
    ubicacion_actual = Column(String(250))
    created_at       = Column(Date, default=date.today)
    updated_at       = Column(Date, default=date.today, onupdate=date.today)

    tipo            = relationship("TipoContenedor",         back_populates="contenedores")
    cliente         = relationship("Cliente",                back_populates="contenedores")
    movimientos     = relationship("Movimiento",             back_populates="contenedor")
    historial       = relationship("HistorialEstado",        back_populates="contenedor")
    fotos           = relationship("FotoContenedor",         back_populates="contenedor")
    facturaciones   = relationship("Facturacion",            back_populates="contenedor")
    arrendamientos  = relationship("ArrendamientoContenedor",back_populates="contenedor")
    ventas          = relationship("VentaContenedor",        back_populates="contenedor")


# ── Movimientos ───────────────────────────────────────────────────────────────
class Movimiento(Base):
    __tablename__ = "Movimientos"

    id_movimiento     = Column(Integer,  primary_key=True, index=True)
    id_contenedor     = Column(Integer,  ForeignKey("Contenedores.id_contenedor"), nullable=False)
    id_usuario        = Column(Integer,  ForeignKey("Usuarios.id_usuario"),        nullable=False)
    fecha_hora        = Column(DateTime, default=datetime.now)
    ubicacion_origen  = Column(String(250))
    ubicacion_destino = Column(String(250))
    medio_transporte  = Column(String(100))
    responsable       = Column(String(100))

    contenedor = relationship("Contenedor", back_populates="movimientos")
    usuario    = relationship("Usuario",    back_populates="movimientos")


# ── Historial de Estado ───────────────────────────────────────────────────────
class HistorialEstado(Base):
    __tablename__ = "Historial_Estado"

    id_historial  = Column(Integer, primary_key=True, index=True)
    id_contenedor = Column(Integer, ForeignKey("Contenedores.id_contenedor"), nullable=False)
    estado        = Column(String(50), nullable=False)
    fecha_inicio  = Column(Date, nullable=False)
    fecha_fin     = Column(Date)

    contenedor = relationship("Contenedor", back_populates="historial")


# ── Fotos Contenedor ──────────────────────────────────────────────────────────
class FotoContenedor(Base):
    __tablename__ = "Fotos_Contenedor"

    id_foto       = Column(Integer, primary_key=True, index=True)
    id_contenedor = Column(Integer, ForeignKey("Contenedores.id_contenedor"), nullable=False)
    ruta_imagen   = Column(String(250), nullable=False)
    fecha_subida  = Column(Date, default=date.today)

    contenedor = relationship("Contenedor", back_populates="fotos")


# ── Facturación ───────────────────────────────────────────────────────────────
class Facturacion(Base):
    __tablename__ = "Facturacion"

    id_factura        = Column(Integer, primary_key=True, index=True)
    id_contenedor     = Column(Integer, ForeignKey("Contenedores.id_contenedor"), nullable=False)
    fecha_facturacion = Column(Date, default=date.today)
    monto             = Column(Float, nullable=False)
    observaciones     = Column(String(250))

    contenedor = relationship("Contenedor", back_populates="facturaciones")


# ── Arrendamiento ─────────────────────────────────────────────────────────────
class ArrendamientoContenedor(Base):
    __tablename__ = "Arrendamiento_Contenedor"

    id_arrendamiento     = Column(Integer, primary_key=True, index=True)
    id_cliente           = Column(Integer, ForeignKey("Clientes.id_cliente"),        nullable=False)
    id_contenedor        = Column(Integer, ForeignKey("Contenedores.id_contenedor"), nullable=False)
    fecha_inicio         = Column(Date, nullable=False)
    fecha_fin            = Column(Date)
    valor_alquiler       = Column(Float, nullable=False)
    estado_arrendamiento = Column(String(30), nullable=False)

    cliente    = relationship("Cliente",    back_populates="arrendamientos")
    contenedor = relationship("Contenedor", back_populates="arrendamientos")


# ── Venta ─────────────────────────────────────────────────────────────────────
class VentaContenedor(Base):
    __tablename__ = "Venta_Contenedor"

    id_venta      = Column(Integer, primary_key=True, index=True)
    id_contenedor = Column(Integer, ForeignKey("Contenedores.id_contenedor"), nullable=False)
    id_cliente    = Column(Integer, ForeignKey("Clientes.id_cliente"),        nullable=False)
    fecha_venta   = Column(Date, default=date.today)
    precio        = Column(Float, nullable=False)

    contenedor = relationship("Contenedor", back_populates="ventas")
    cliente    = relationship("Cliente",    back_populates="ventas")
