#!/usr/bin/env python
"""
Script para diagnosticar el error en login
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Usuario
from auth.hashing import verify_password
from auth.jwt import create_access_token

print("=" * 60)
print("🔍 Diagnosticando endpoint de login...")
print("=" * 60)

try:
    db = SessionLocal()
    
    # 1. Verificar que existe el usuario
    print("\n1️⃣  Buscando usuario 'admin'...")
    usuario = db.query(Usuario).filter(Usuario.user == "admin").first()
    
    if not usuario:
        print("   ❌ Usuario no encontrado")
    else:
        print(f"   ✅ Usuario encontrado:")
        print(f"      - ID: {usuario.id_usuario}")
        print(f"      - Nombre: {usuario.nombres}")
        print(f"      - Rol: {usuario.rol}")
        print(f"      - Password hash: {usuario.password[:50]}...")
    
    # 2. Verificar contraseña
    print("\n2️⃣  Verificando contraseña...")
    try:
        is_valid = verify_password("admin123", usuario.password)
        if is_valid:
            print("   ✅ Contraseña válida")
        else:
            print("   ❌ Contraseña inválida")
    except Exception as e:
        print(f"   ❌ Error verificando contraseña: {e}")
    
    # 3. Crear token
    print("\n3️⃣  Creando token JWT...")
    try:
        token = create_access_token(user=usuario.user, role=usuario.rol)
        print(f"   ✅ Token creado exitosamente")
        print(f"      Token: {token[:50]}...")
    except Exception as e:
        print(f"   ❌ Error creando token: {e}")
        import traceback
        traceback.print_exc()
    
    db.close()
    print("\n✅ Diagnóstico completado")
    
except Exception as e:
    print(f"\n❌ Error general: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
