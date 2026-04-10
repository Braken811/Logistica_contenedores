#!/usr/bin/env python
# scripts/hash_existing_passwords.py
# Ejecutar UNA SOLA VEZ: python scripts/hash_existing_passwords.py

import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Usuario
from auth.hashing import hash_password

db = SessionLocal()

# Hashear contraseñas de usuarios
usuarios_actualizados = 0
for usuario in db.query(Usuario).all():
    # Evitar doble hash: las contraseñas hasheadas con bcrypt comienzan con $2b$
    if not usuario.password.startswith('$2b$'):
        usuario.password = hash_password(usuario.password)
        usuarios_actualizados += 1

db.commit()
db.close()
print(f'✓ {usuarios_actualizados} contraseña(s) actualizada(s) correctamente.')
