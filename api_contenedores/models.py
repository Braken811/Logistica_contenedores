from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from schemas import EstadoContenedor, RolUsuario
from datetime import datetime

# Usuarios
class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombres = Column(String, nullable=False)
    apellidos = Column(String)
    email = Column(String)
    user = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    rol = Column(SQLEnum(RolUsuario), nullable=False)

# Clientes
class Cliente(Base):
    __tablename__ = "clientes"

    id_cliente = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    nit = Column(String, unique=True, nullable=False)
    telefono = Column(String)
    email = Column(String)
    direccion = Column(String)

# Tipos de Contenedores
class TipoContenedor(Base):
    __tablename__ = "tipos_contenedores"

    id_tipo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)

# Contenedores
class Contenedor(Base):
    __tablename__ = "contenedores"

    id_contenedor = Column(Integer, primary_key=True, index=True)
    id_codigo = Column(String, unique=True, nullable=False)
    id_tipo = Column(Integer, ForeignKey("tipos_contenedores.id_tipo"), nullable=False)
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente"), nullable=False)
    estado = Column(SQLEnum(EstadoContenedor), nullable=False)
    ubicacion_actual = Column(String)
    created_at = Column(Date)
    updated_at = Column(Date)

    tipo = relationship("TipoContenedor")
    cliente = relationship("Cliente")

# Movimientos
class Movimiento(Base):
    __tablename__ = "movimientos"

    id_movimiento = Column(Integer, primary_key=True, index=True)
    id_contenedor = Column(Integer, ForeignKey("contenedores.id_contenedor"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    fecha_hora = Column(DateTime, default=datetime.utcnow)
    ubicacion_origen = Column(String)
    ubicacion_destino = Column(String)
    medio_transporte = Column(String)
    responsable = Column(String)

    contenedor = relationship("Contenedor")
    usuario = relationship("Usuario")

# Historial de Estado
class HistorialEstado(Base):
    __tablename__ = "historial_estado"

    id_historial = Column(Integer, primary_key=True, index=True)
    id_contenedor = Column(Integer, ForeignKey("contenedores.id_contenedor"), nullable=False)
    estado = Column(SQLEnum(EstadoContenedor), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date)

    contenedor = relationship("Contenedor")

# Fotos
class Foto(Base):
    __tablename__ = "fotos"

    id_foto = Column(Integer, primary_key=True, index=True)
    id_contenedor = Column(Integer, ForeignKey("contenedores.id_contenedor"), nullable=False)
    ruta_imagen = Column(String, nullable=False)
    fecha_subida = Column(Date, default=datetime.utcnow().date)

    contenedor = relationship("Contenedor")

# Facturación
class Facturacion(Base):
    __tablename__ = "facturacion"

    id_factura = Column(Integer, primary_key=True, index=True)
    id_contenedor = Column(Integer, ForeignKey("contenedores.id_contenedor"), nullable=False)
    fecha_facturacion = Column(Date, default=datetime.utcnow().date)
    monto = Column(Float, nullable=False)
    observaciones = Column(String)

    contenedor = relationship("Contenedor")

# Arrendamiento
class Arrendamiento(Base):
    __tablename__ = "arrendamiento"

    id_arrendamiento = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente"), nullable=False)
    id_contenedor = Column(Integer, ForeignKey("contenedores.id_contenedor"), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date)
    valor_alquiler = Column(Float, nullable=False)
    estado_arrendamiento = Column(String, nullable=False)

    cliente = relationship("Cliente")
    contenedor = relationship("Contenedor")

# Ventas
class Venta(Base):
    __tablename__ = "ventas"

    id_venta = Column(Integer, primary_key=True, index=True)
    id_contenedor = Column(Integer, ForeignKey("contenedores.id_contenedor"), nullable=False)
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente"), nullable=False)
    fecha_venta = Column(Date, default=datetime.utcnow().date)
    precio = Column(Float, nullable=False)

    contenedor = relationship("Contenedor")
    cliente = relationship("Cliente")