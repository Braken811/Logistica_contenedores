from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey, Boolean, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from schemas import EstadoContenedor
from datetime import datetime


# Usuarios
class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario       = Column(Integer, primary_key=True, index=True)
    nombres          = Column(String, nullable=False)
    apellidos        = Column(String)
    email            = Column(String)
    user             = Column(String, unique=True, nullable=False)
    password         = Column(String, nullable=False)
    rol              = Column(String, nullable=False)
    email_verificado   = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    ruta_imagen        = Column(String, nullable=True)

    movimientos = relationship("Movimiento", cascade="all, delete-orphan")
    notificaciones = relationship("Notificacion", cascade="all, delete-orphan")


# Clientes
class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente = Column(Integer, primary_key=True, index=True)
    nombre     = Column(String, nullable=False)
    nit        = Column(String, unique=True, nullable=False)
    telefono   = Column(String)
    email      = Column(String)
    direccion  = Column(String)


# Tipos de Contenedores
class TipoContenedor(Base):
    __tablename__ = "tipos_contenedores"

    id_tipo     = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String, nullable=False)
    descripcion = Column(String)


# Contenedores
class Contenedor(Base):
    __tablename__ = "contenedores"

    id_contenedor    = Column(Integer, primary_key=True, index=True)
    id_codigo        = Column(String, unique=True, nullable=False)
    id_tipo          = Column(Integer, ForeignKey("tipos_contenedores.id_tipo"), nullable=False)
    id_cliente       = Column(Integer, ForeignKey("clientes.id_cliente"), nullable=True)
    estado           = Column(SQLEnum(EstadoContenedor), nullable=False)
    ubicacion_actual = Column(String)
    ruta_imagen      = Column(String)
    created_at       = Column(Date)
    updated_at       = Column(Date)

    tipo       = relationship("TipoContenedor")
    cliente    = relationship("Cliente")
    movimientos = relationship("Movimiento", cascade="all, delete-orphan")
    historial  = relationship("HistorialEstado", cascade="all, delete-orphan")
    arrendamientos = relationship("Arrendamiento", cascade="all, delete-orphan")
    facturacion = relationship("Facturacion", cascade="all, delete-orphan")


# Movimientos
class Movimiento(Base):
    __tablename__ = "movimientos"

    id_movimiento     = Column(Integer, primary_key=True, index=True)
    id_contenedor     = Column(Integer, ForeignKey("contenedores.id_contenedor"), nullable=False)
    id_usuario        = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    fecha_hora        = Column(DateTime, default=datetime.utcnow)
    fecha_salida      = Column(Date, nullable=True)
    ubicacion_origen  = Column(String)
    ubicacion_destino = Column(String)
    medio_transporte  = Column(String)
    responsable       = Column(String)

    contenedor = relationship("Contenedor")
    usuario    = relationship("Usuario")


# Historial de Estado
class HistorialEstado(Base):
    __tablename__ = "historial_estado"

    id_historial  = Column(Integer, primary_key=True, index=True)
    id_contenedor = Column(Integer, ForeignKey("contenedores.id_contenedor"), nullable=False)
    estado        = Column(SQLEnum(EstadoContenedor), nullable=False)
    fecha_inicio  = Column(Date, nullable=False)
    fecha_fin     = Column(Date)

    contenedor = relationship("Contenedor")


# Fotos
class Foto(Base):
    __tablename__ = "fotos"

    id_foto       = Column(Integer, primary_key=True, index=True)
    id_contenedor = Column(Integer, ForeignKey("contenedores.id_contenedor"), nullable=False)
    ruta_imagen   = Column(String, nullable=False)
    fecha_subida  = Column(Date, default=datetime.utcnow().date)

    contenedor = relationship("Contenedor")


# Facturación
class Facturacion(Base):
    __tablename__ = "facturacion"

    id_factura        = Column(Integer, primary_key=True, index=True)
    id_contenedor     = Column(Integer, ForeignKey("contenedores.id_contenedor"), nullable=False)
    fecha_facturacion = Column(Date, default=datetime.utcnow().date)
    monto             = Column(Float, nullable=False)
    observaciones     = Column(String)
    codigo_factura    = Column(String)
    fecha_vencimiento = Column(Date)
    estado_pago       = Column(String, default="pendiente")
    id_arrendamiento  = Column(Integer, ForeignKey("arrendamiento.id_arrendamiento"), nullable=True)

    contenedor    = relationship("Contenedor")
    arrendamiento = relationship("Arrendamiento")


# Arrendamiento
class Arrendamiento(Base):
    __tablename__ = "arrendamiento"

    id_arrendamiento     = Column(Integer, primary_key=True, index=True)
    id_cliente           = Column(Integer, ForeignKey("clientes.id_cliente"), nullable=False)
    id_contenedor        = Column(Integer, ForeignKey("contenedores.id_contenedor"), nullable=False)
    fecha_inicio         = Column(Date, nullable=False)
    fecha_fin            = Column(Date)
    valor_alquiler       = Column(Float, nullable=False)
    estado_arrendamiento = Column(String, nullable=False)

    cliente    = relationship("Cliente")
    contenedor = relationship("Contenedor")


# Ventas
class Venta(Base):
    __tablename__ = "ventas"

    id_venta      = Column(Integer, primary_key=True, index=True)
    id_contenedor = Column(Integer, ForeignKey("contenedores.id_contenedor"), nullable=False)
    id_cliente    = Column(Integer, ForeignKey("clientes.id_cliente"), nullable=False)
    fecha_venta   = Column(Date, default=datetime.utcnow().date)
    precio        = Column(Float, nullable=False)

    contenedor = relationship("Contenedor")
    cliente    = relationship("Cliente")


# Notificaciones
class Notificacion(Base):
    __tablename__ = "notificaciones"
    __table_args__ = (
        UniqueConstraint("id_usuario", "ref_id", name="uq_notif_user_ref"),
    )

    id_notificacion = Column(Integer, primary_key=True, index=True)
    id_usuario      = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    tipo            = Column(String, nullable=False)   # 'error' | 'warn' | 'info'
    titulo          = Column(String, nullable=False)
    mensaje         = Column(String)
    fecha           = Column(DateTime, default=datetime.utcnow)
    leido           = Column(Boolean, default=False)
    fecha_lectura   = Column(DateTime, nullable=True)
    ref_id          = Column(String, nullable=True)    # clave estable para deduplicar

    usuario = relationship("Usuario")
