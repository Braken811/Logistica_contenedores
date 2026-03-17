"""
Configuración de conexión a SQL Server.
Usa variables de entorno definidas en el archivo .env
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# ── Cadena de conexión ────────────────────────────────────────────────────────
# Formato: mssql+pyodbc://user:password@server/database?driver=ODBC+Driver+17+for+SQL+Server
DB_SERVER   = os.getenv("DB_SERVER",   "localhost")
DB_NAME     = os.getenv("DB_NAME",     "Gestion_Contenedores")
DB_USER     = os.getenv("DB_USER",     "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "tu_password")
DB_DRIVER   = os.getenv("DB_DRIVER",   "ODBC+Driver+17+for+SQL+Server")

DATABASE_URL = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"
    f"?driver={DB_DRIVER}"
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency que provee la sesión de base de datos a cada endpoint."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Verifica la conexión a la base de datos al iniciar."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅  Conexión a SQL Server establecida correctamente.")
    except Exception as e:
        print(f"❌  Error al conectar con SQL Server: {e}")
