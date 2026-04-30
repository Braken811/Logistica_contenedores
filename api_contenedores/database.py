import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de PostgreSQL
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "logistica_contenedores")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "postgres")

DATABASE_URL = f"postgresql+psycopg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

logger.info(f"📦 Conectando a BD: {DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}")

# Crear engine con configuración optimizada
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para debug SQL
    pool_pre_ping=True,  # Verifica conexión antes de usar
    pool_recycle=3600,   # Recicla conexiones cada hora
)

# Event listener para conexión exitosa
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    logger.info("✅ Conexión a PostgreSQL exitosa")

# Event listener para errores
@event.listens_for(engine, "engine_disposed")
def receive_engine_disposed(engine):
    logger.info("⚠️ Motor de BD descartado")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Importar modelos
import models

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear todas las tablas en la base de datos
def init_db():
    """Inicializa las tablas de la base de datos"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Base de datos inicializada correctamente")
        
        # Verificar que podemos conectar
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("✅ Verificación de conexión: OK")
    except Exception as e:
        logger.error(f"❌ Error inicializando BD: {e}")
        raise

# Llamar al inicializar el módulo
init_db()
