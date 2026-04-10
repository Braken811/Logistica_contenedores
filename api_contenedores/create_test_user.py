#!/usr/bin/env python
"""
Script para crear un usuario de prueba en la base de datos
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Usuario
from auth.hashing import hash_password
from schemas import RolUsuario

db = SessionLocal()

try:
    # Verificar si ya existe el usuario
    existing_user = db.query(Usuario).filter(Usuario.user == "admin").first()
    
    if existing_user:
        print(f"ℹ️  Usuario 'admin' ya existe")
        print(f"   Rol actual: {existing_user.rol}")
    else:
        # Crear nuevo usuario
        new_user = Usuario(
            user="admin",
            password=hash_password("admin123"),
            rol=RolUsuario.admin,
            nombres="Administrador",
            apellidos="Sistema",
            email="admin@logistica.com"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"✅ Usuario 'admin' creado exitosamente")
        print(f"   ID: {new_user.id_usuario}")
        print(f"   Usuario: {new_user.user}")
        print(f"   Rol: {new_user.rol}")
        print(f"\n   Puedes hacer login con:")
        print(f"   - Usuario: admin")
        print(f"   - Contraseña: admin123")
        
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
