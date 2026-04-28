#!/usr/bin/env python
"""Test script para diagnosticar error en login"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api/auth/login"

# Intentar login
print("=" * 60)
print("🔐 Probando endpoint de login")
print("=" * 60)
print(f"\nURL: {API_URL}")
print("Usuario: admin")
print("Contraseña: admin123\n")

login_data = {
    "user": "admin",
    "password": "admin123"
}

try:
    print("📤 Enviando solicitud...")
    response = requests.post(
        API_URL,
        json=login_data,
        timeout=10,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"✅ Respuesta recibida")
    print(f"Status Code: {response.status_code}")
    print(f"\nHeaders:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    print(f"\nResponse Body:")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    if response.status_code == 200:
        print("\n✅ ¡LOGIN EXITOSO!")
        print(f"   Access Token: {data.get('access_token', 'NO TOKEN')[:50]}...")
        print(f"   Role: {data.get('role', 'NO ROLE')}")
        print(f"   Token Type: {data.get('token_type', 'NO TYPE')}")
    else:
        print(f"\n❌ Error en login: {response.status_code}")
        if 'detail' in data:
            print(f"   Detalle: {data['detail']}")
        
except requests.exceptions.ConnectionError as e:
    print(f"❌ Error de conexión: No se puede conectar a {API_URL}")
    print(f"   ¿El API está corriendo?")
    print(f"   {e}")
except requests.exceptions.Timeout:
    print(f"❌ Timeout: La solicitud tardó más de 10 segundos")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
