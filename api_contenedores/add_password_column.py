#!/usr/bin/env python
"""
Script para agregar columna password a tabla usuarios
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine
import sqlalchemy as sa

print("=" * 60)
print("🔧 Agregando columna password a tabla usuarios...")
print("=" * 60)

try:
    with engine.connect() as conn:
        # Verificar si la columna ya existe
        inspector = sa.inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('usuarios')]
        
        if 'password' in columns:
            print("ℹ️  La columna 'password' ya existe en la tabla usuarios")
        else:
            # Agregar columna password
            conn.execute(sa.text(
                "ALTER TABLE usuarios ADD COLUMN password VARCHAR NOT NULL DEFAULT ''"
            ))
            conn.commit()
            print("✅ Columna 'password' agregada exitosamente")
        
        print("\n✅ ¡Completado!")
        
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
