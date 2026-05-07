#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la conexión a la base de datos.
Uso: python test_database_connection.py
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar .env
load_dotenv()

# Variables de conexión
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_NAME = os.getenv("DATABASE_NAME", "contenedores")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "Mmillan.06")

DATABASE_URL = f"postgresql+psycopg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

print("\n" + "="*70)
print("🔍 DIAGNÓSTICO DE CONEXIÓN A BASE DE DATOS")
print("="*70)

print("\n📋 Configuración:")
print(f"  Host: {DATABASE_HOST}")
print(f"  Port: {DATABASE_PORT}")
print(f"  Database: {DATABASE_NAME}")
print(f"  User: {DATABASE_USER}")

try:
    print("\n⏳ Conectando a PostgreSQL...")
    engine = create_engine(DATABASE_URL, echo=False)
    
    # Test 1: Verificar conexión básica
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ Conexión exitosa a PostgreSQL")
        print(f"   Versión: {version.split(',')[0]}")
    
    # Test 2: Listar tablas
    print("\n📊 Tablas en la base de datos:")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        print("  ⚠️  No hay tablas en la base de datos")
    else:
        for table in tables:
            columns = inspector.get_columns(table)
            print(f"  ✅ {table} ({len(columns)} columnas)")
    
    # Test 3: Contar registros
    print("\n📈 Conteo de registros:")
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # Importar modelos
    from models import (
        Usuario, Cliente, TipoContenedor, Contenedor,
        Movimiento, HistorialEstado, Foto, Arrendamiento,
        Facturacion, Venta
    )
    
    models_to_check = [
        ("Usuarios", Usuario),
        ("Clientes", Cliente),
        ("Tipos de Contenedores", TipoContenedor),
        ("Contenedores", Contenedor),
        ("Movimientos", Movimiento),
        ("Historial de Estado", HistorialEstado),
        ("Fotos", Foto),
        ("Arrendamientos", Arrendamiento),
        ("Facturas", Facturacion),
        ("Ventas", Venta),
    ]
    
    for name, model in models_to_check:
        count = db.query(model).count()
        print(f"  {name}: {count} registros")
    
    db.close()
    
    print("\n✅ DIAGNÓSTICO COMPLETADO - TODO CORRECTO")
    print("="*70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n💡 Soluciones posibles:")
    print("  1. Verificar que PostgreSQL está corriendo: sudo service postgresql start")
    print("  2. Verificar credenciales en .env")
    print("  3. Crear la base de datos: createdb contenedores")
    print("  4. Verificar firewall/conexión de red")
    print("\n" + "="*70)
    sys.exit(1)
