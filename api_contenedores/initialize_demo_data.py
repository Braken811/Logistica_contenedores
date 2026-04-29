#!/usr/bin/env python
"""
Script para inicializar la base de datos con datos de prueba
Ejecutar: python initialize_demo_data.py
"""

from database import SessionLocal
from models import Cliente, TipoContenedor
import sys

def add_demo_data():
    db = SessionLocal()
    try:
        print("\n" + "="*60)
        print("  INICIALIZANDO BASE DE DATOS CON DATOS DE PRUEBA")
        print("="*60)

        # Crear Tipos de Contenedores
        print("\n1. Agregando tipos de contenedores...")
        tipos = [
            TipoContenedor(nombre="Contenedor 20ft", descripcion="Contenedor estándar de 20 pies"),
            TipoContenedor(nombre="Contenedor 40ft", descripcion="Contenedor estándar de 40 pies"),
            TipoContenedor(nombre="High Cube 40ft", descripcion="Contenedor de 40 pies con mayor altura"),
            TipoContenedor(nombre="Flatbed", descripcion="Contenedor plano para carga especial"),
        ]

        for tipo in tipos:
            if not db.query(TipoContenedor).filter(TipoContenedor.nombre == tipo.nombre).first():
                db.add(tipo)
                print(f"   ✓ {tipo.nombre}")

        # Crear Clientes
        print("\n2. Agregando clientes...")
        clientes = [
            Cliente(
                nombre="Transportes Globales S.A.",
                nit="900.123.456-7",
                telefono="+57 300 1234567",
                email="contacto@transportesglobales.co",
                direccion="Calle 10 #20-30, Barranquilla"
            ),
            Cliente(
                nombre="Logística Internacional Ltd.",
                nit="800.234.567-8",
                telefono="+57 301 2345678",
                email="info@logisticaint.co",
                direccion="Carrera 5 #15-40, Cartagena"
            ),
            Cliente(
                nombre="Puerto de Servicios Colombia",
                nit="700.345.678-9",
                telefono="+57 302 3456789",
                email="puertodeservicios@psc.co",
                direccion="Zona Portuaria, Santa Marta"
            ),
            Cliente(
                nombre="Comercio Exterior Express",
                nit="600.456.789-0",
                telefono="+57 303 4567890",
                email="comercioext@cee.co",
                direccion="Avenida Maritima #50, Buenaventura"
            ),
        ]

        for cliente in clientes:
            if not db.query(Cliente).filter(Cliente.nit == cliente.nit).first():
                db.add(cliente)
                print(f"   ✓ {cliente.nombre}")

        # Commit
        db.commit()

        # Verificar los datos
        print("\n3. Verificando datos insertados...")
        tipos_count = db.query(TipoContenedor).count()
        clientes_count = db.query(Cliente).count()

        print(f"\n   Total tipos de contenedores: {tipos_count}")
        print(f"   Total clientes: {clientes_count}")

        print("\n" + "="*60)
        print("  BASE DE DATOS INICIALIZADA CORRECTAMENTE")
        print("="*60)
        print("\nAhora puedes:")
        print("  1. Ejecutar: python test_api_completa.py")
        print("  2. O acceder a: http://localhost:8000/docs")
        print("="*60 + "\n")

        return True

    except Exception as e:
        print(f"\nError: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = add_demo_data()
    sys.exit(0 if success else 1)
