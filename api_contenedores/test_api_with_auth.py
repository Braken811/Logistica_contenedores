#!/usr/bin/env python3
"""
Script para probar la API completa con autenticación JWT.
Uso: python test_api_with_auth.py
"""

import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000"

# 🎨 Colores para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def test_section(title):
    print(f"\n{CYAN}{'='*70}")
    print(f"🧪 {title}")
    print(f"{'='*70}{RESET}\n")

def success(msg):
    print(f"{GREEN}✅ {msg}{RESET}")

def error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def info(msg):
    print(f"{YELLOW}ℹ️  {msg}{RESET}")

def print_response(response, title="Response"):
    print(f"\n{CYAN}{title}:{RESET}")
    print(f"  Status: {response.status_code}")
    try:
        data = response.json()
        print(f"  Body: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"  Body: {response.text}")

# ============================================================================
test_section("1. CREAR USUARIO ADMIN INICIAL (Bootstrap)")

try:
    response = requests.post(
        f"{BASE_URL}/usuarios/public",
        json={
            "nombres": "Admin",
            "apellidos": "Sistema",
            "email": "admin@logistica.com",
            "user": "admin",
            "password": "admin123",
        }
    )
    
    if response.status_code in [201, 403]:
        if response.status_code == 403:
            info("Admin ya existe (esperado si no es primera ejecución)")
        else:
            success("Usuario admin creado")
            print_response(response)
    else:
        error(f"Error: {response.status_code}")
        print_response(response)
except Exception as e:
    error(f"Error de conexión: {e}")
    info("Asegúrate de que la API está corriendo: uvicorn main:app --reload")

# ============================================================================
test_section("2. LOGIN - Obtener TOKEN")

token = None
try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "user": "admin",
            "password": "admin123",
        }
    )
    
    if response.status_code == 200:
        success("Login exitoso")
        data = response.json()
        token = data.get("access_token")
        print_response(response, "Login Response")
        info(f"Token obtenido: {token[:50]}...")
    else:
        error(f"Login fallido: {response.status_code}")
        print_response(response)
except Exception as e:
    error(f"Error: {e}")

if not token:
    error("No se pudo obtener token. Abortando pruebas.")
    exit(1)

# Headers con token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# ============================================================================
test_section("3. CREAR CLIENTE")

cliente_id = None
try:
    response = requests.post(
        f"{BASE_URL}/clientes",
        headers=headers,
        json={
            "nombre": "Test Cliente SA",
            "nit": "123456789",
            "telefono": "555-1234",
            "email": "cliente@test.com",
            "direccion": "Calle 1 #100"
        }
    )
    
    if response.status_code == 201:
        success("Cliente creado")
        data = response.json()
        cliente_id = data.get("id_cliente")
        print_response(response)
        info(f"Cliente ID: {cliente_id}")
    else:
        error(f"Error: {response.status_code}")
        print_response(response)
except Exception as e:
    error(f"Error: {e}")

# ============================================================================
test_section("4. CREAR TIPO DE CONTENEDOR")

tipo_id = None
try:
    response = requests.post(
        f"{BASE_URL}/tipos-contenedores",
        headers=headers,
        json={
            "nombre": "Container 20ft",
            "descripcion": "Contenedor estándar de 20 pies"
        }
    )
    
    if response.status_code == 201:
        success("Tipo de contenedor creado")
        data = response.json()
        tipo_id = data.get("id_tipo")
        print_response(response)
        info(f"Tipo ID: {tipo_id}")
    else:
        error(f"Error: {response.status_code}")
        print_response(response)
except Exception as e:
    error(f"Error: {e}")

# ============================================================================
if cliente_id and tipo_id:
    test_section("5. CREAR CONTENEDOR")
    
    contenedor_id = None
    try:
        response = requests.post(
            f"{BASE_URL}/contenedores",
            headers=headers,
            json={
                "id_codigo": f"CONT-TEST-{date.today()}",
                "id_tipo": tipo_id,
                "id_cliente": cliente_id,
                "estado": "disponible",
                "ubicacion_actual": "Puerto de Barranquilla"
            }
        )
        
        if response.status_code == 201:
            success("Contenedor creado")
            data = response.json()
            contenedor_id = data.get("id_contenedor")
            print_response(response)
            info(f"Contenedor ID: {contenedor_id}")
        else:
            error(f"Error: {response.status_code}")
            print_response(response)
    except Exception as e:
        error(f"Error: {e}")
    
    # ========================================================================
    if contenedor_id:
        test_section("6. REGISTRAR MOVIMIENTO")
        
        try:
            response = requests.post(
                f"{BASE_URL}/movimientos",
                headers=headers,
                json={
                    "id_contenedor": contenedor_id,
                    "id_usuario": 1,
                    "ubicacion_origen": "Puerto de Barranquilla",
                    "ubicacion_destino": "Bogotá",
                    "medio_transporte": "Camión",
                    "responsable": "Juan Pérez"
                }
            )
            
            if response.status_code == 201:
                success("Movimiento registrado")
                print_response(response)
            else:
                error(f"Error: {response.status_code}")
                print_response(response)
        except Exception as e:
            error(f"Error: {e}")

# ============================================================================
test_section("7. LISTAR CONTENEDORES (CON PROTECCIÓN JWT)")

try:
    response = requests.get(
        f"{BASE_URL}/contenedores",
        headers=headers
    )
    
    if response.status_code == 200:
        success("Listado de contenedores obtenido")
        data = response.json()
        info(f"Total de contenedores: {len(data)}")
        print_response(response)
    else:
        error(f"Error: {response.status_code}")
        print_response(response)
except Exception as e:
    error(f"Error: {e}")

# ============================================================================
test_section("8. PROBAR ACCESO SIN TOKEN (Debe fallar)")

try:
    response = requests.get(f"{BASE_URL}/contenedores")
    
    if response.status_code == 403:
        success("Acceso denegado sin token (comportamiento esperado)")
        print_response(response)
    else:
        error(f"Acceso no protegido: {response.status_code}")
except Exception as e:
    error(f"Error: {e}")

# ============================================================================
test_section("RESUMEN")
print(f"""
{GREEN}✅ Pruebas completadas{RESET}

Si todos los tests pasaron:
1. ✅ La BD está conectada correctamente
2. ✅ Los tokens JWT están protegiendo los endpoints
3. ✅ Los datos se están guardando en la BD

Próximos pasos:
- Revisar logs de la API para más detalles
- Usar /docs para explorar todos los endpoints
- Actualizar el frontend para enviar tokens en los headers

Documentación:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
""")
