#!/usr/bin/env python
"""
Script para generar hash argon2 de la contraseña admin123
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.hashing import hash_password
from database import SessionLocal
from models import Usuario
import sqlalchemy as sa

print("=" * 60)
print("🔐 Generando hash argon2 para 'admin123'...")
print("=" * 60)

# Generar nuevo hash
new_hash = hash_password("admin123")
print(f"\n✅ Hash generado: {new_hash}")

# Actualizar en la BD
print("\n📝 Actualizando BD...")
db = SessionLocal()

try:
    # Actualizar usuario admin
    admin = db.query(Usuario).filter(Usuario.user == "admin").first()
    
    if admin:
        admin.password = new_hash
        db.commit()
        print("✅ Usuario 'admin' actualizado en BD")
        print(f"\n🔑 Credenciales:")
        print(f"   Usuario: admin")
        print(f"   Contraseña: admin123")
        print(f"\n💡 Ya puedes hacer login con estas credenciales")
    else:
        print("❌ Usuario 'admin' no encontrado")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
