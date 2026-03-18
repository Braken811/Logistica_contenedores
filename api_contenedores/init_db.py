#!/usr/bin/env python3
"""
Script para inicializar la base de datos PostgreSQL.
Ejecuta este script para crear todas las tablas necesarias.
"""

from database import Base, engine

def init_database():
    print("Creando tablas en la base de datos PostgreSQL...")
    Base.metadata.create_all(bind=engine)
    print("¡Tablas creadas exitosamente!")

if __name__ == "__main__":
    init_database()