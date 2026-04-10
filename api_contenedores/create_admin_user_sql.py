#!/usr/bin/env python
"""
Script para crear usuario de prueba directamente con SQL
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine
import sqlalchemy as sa

# Hash de "admin123" generado con bcrypt (costo=12)
# Formato: $2b$12$[22-char salt][31-char hash]
HASHED_PASSWORD = "$2b$12$8pQVswA6Fwu7CYNQz3fKTOdddKKHpTD4ScXHxnMKFzXHyZ8F8wd1W"

print("=" * 60)
print("👤 Creando usuario admin de prueba...")
print("=" * 60)

try:
    with engine.connect() as conn:
        # Insertar usuario admin
        conn.execute(sa.text("""
            INSERT INTO usuarios (nombres, apellidos, email, "user", password, rol)
            VALUES (:nombres, :apellidos, :email, :user, :password, :rol)
            ON CONFLICT ("user") DO UPDATE SET password = :password
        """), {
            "nombres": "Administrador",
            "apellidos": "Sistema",
            "email": "admin@logistica.com",
            "user": "admin",
            "password": HASHED_PASSWORD,
            "rol": "admin"
        })
        conn.commit()
        
        print("✅ Usuario 'admin' creado/actualizado exitosamente")
        print("\n🔑 Credenciales:")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        print("\n💡 Puedes usar estas credenciales en POST /auth/login")
        
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
