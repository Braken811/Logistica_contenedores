#!/usr/bin/env python
"""
Script para resetear la tabla usuarios (borrar y recrear)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base
from models import Usuario

print("=" * 60)
print("🔧 Eliminando y recreando tabla usuarios...")
print("=" * 60)

try:
    # Borrar tabla usuarios si existe
    Usuario.__table__.drop(engine, checkfirst=True)
    print("✅ Tabla usuarios eliminada")
    
    # Recrear tabla usuarios
    Usuario.__table__.create(engine, checkfirst=True)
    print("✅ Tabla usuarios recreada con todas las columnas")
    
    print("\n✅ ¡Completado!")
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
