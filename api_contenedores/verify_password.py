#!/usr/bin/env python
"""
Script para verificar que el hash de la contraseña es válido
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.hashing import verify_password, hash_password
from database import SessionLocal
from models import Usuario

# Contraseña a probar
password_to_test = "admin123"

# Hash que se almacenó en la BD
stored_hash = "$2b$12$8pQVswA6Fwu7CYNQz3fKTOdddKKHpTD4ScXHxnMKFzXHyZ8F8wd1W"

print("=" * 60)
print("🔐 Verificando hash de contraseña")
print("=" * 60)

print(f"\nContraseña a probar: {password_to_test}")
print(f"Hash almacenado: {stored_hash}")

# Verificar
try:
    result = verify_password(password_to_test, stored_hash)
    print(f"\n✅ Resultado: {result}")
    
    if result:
        print("\n✅ ¡La contraseña es CORRECTA!")
    else:
        print("\n❌ ¡La contraseña NO coincide!")
        
except Exception as e:
    print(f"\n❌ Error verificando: {e}")
    import traceback
    traceback.print_exc()

# También verificar en BD
print("\n" + "=" * 60)
print("Verificando usuario en BD...")
print("=" * 60)

db = SessionLocal()
user = db.query(Usuario).filter(Usuario.user == "admin").first()

if user:
    print(f"✅ Usuario encontrado: {user.user}")
    print(f"   Rol: {user.rol}")
    print(f"   Hash en BD: {user.password}")
    
    # Intentar verificar
    result = verify_password(password_to_test, user.password)
    print(f"\n   Verificación de contraseña: {'✅ CORRECTA' if result else '❌ INCORRECTA'}")
else:
    print("❌ Usuario 'admin' no encontrado en BD")

db.close()
