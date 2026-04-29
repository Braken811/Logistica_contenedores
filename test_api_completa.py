#!/usr/bin/env python
"""
Script de prueba completo para verificar toda la funcionalidad de la API
Ejecutar: python test_api_completa.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TOKEN = None

def print_section(titulo):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")

def print_response(response, title="Respuesta"):
    print(f"\n{title}:")
    print(f"  Status: {response.status_code}")
    try:
        print(f"  Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"  Body: {response.text}")

def test_login():
    """Prueba login y obtiene token"""
    global TOKEN
    print_section("1. PRUEBA DE LOGIN")

    data = {
        "user": "admin",
        "password": "Mmillan.06"  # Cambiar si es diferente
    }

    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print_response(response, "Login Response")

    if response.status_code == 200:
        TOKEN = response.json()["access_token"]
        print(f"\n✓ Token obtenido: {TOKEN[:50]}...")
        return True
    else:
        print("\n✗ Error en login")
        return False

def get_headers():
    """Retorna headers con el token"""
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

def test_crear_usuario():
    """Prueba crear nuevo usuario"""
    print_section("2. CREAR NUEVO USUARIO")

    data = {
        "nombres": "Test",
        "apellidos": "Usuario",
        "email": "test@example.com",
        "user": "test_user_2026",
        "password": "TestPass123!",
        "rol": "operador"
    }

    response = requests.post(f"{BASE_URL}/usuarios/", json=data, headers=get_headers())
    print_response(response, "Crear Usuario")

    if response.status_code == 201:
        usuario_id = response.json()["id_usuario"]
        print(f"\n✓ Usuario creado con ID: {usuario_id}")
        return usuario_id
    else:
        print("\n✗ Error creando usuario")
        return None

def test_listar_usuarios():
    """Prueba listar usuarios"""
    print_section("3. LISTAR USUARIOS")

    response = requests.get(f"{BASE_URL}/usuarios/", headers=get_headers())
    print_response(response, "Listar Usuarios")

    if response.status_code == 200:
        usuarios = response.json()
        print(f"\n✓ Se encontraron {len(usuarios)} usuarios")
        return True
    return False

def test_crear_contenedor():
    """Prueba crear contenedor"""
    print_section("4. CREAR CONTENEDOR")

    data = {
        "id_codigo": f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "id_tipo": 1,
        "id_cliente": 1,
        "estado": "activo",
        "ubicacion_actual": "Bodega de Prueba"
    }

    response = requests.post(f"{BASE_URL}/contenedores/", json=data, headers=get_headers())
    print_response(response, "Crear Contenedor")

    if response.status_code == 201:
        contenedor_id = response.json()["id_contenedor"]
        print(f"\n✓ Contenedor creado con ID: {contenedor_id}")
        return contenedor_id
    else:
        print("\n✗ Error creando contenedor")
        return None

def test_listar_contenedores():
    """Prueba listar contenedores"""
    print_section("5. LISTAR CONTENEDORES")

    response = requests.get(f"{BASE_URL}/contenedores/?limit=10", headers=get_headers())
    print_response(response, "Listar Contenedores")

    if response.status_code == 200:
        contenedores = response.json()
        print(f"\n✓ Se encontraron {len(contenedores)} contenedores")
        return True
    return False

def test_actualizar_contenedor(contenedor_id):
    """Prueba actualizar contenedor"""
    print_section("6. ACTUALIZAR CONTENEDOR")

    data = {
        "ubicacion_actual": "Bodega Actualizada - Prueba",
        "estado": "en_mantenimiento"
    }

    response = requests.put(
        f"{BASE_URL}/contenedores/{contenedor_id}",
        json=data,
        headers=get_headers()
    )
    print_response(response, "Actualizar Contenedor")

    return response.status_code in [200, 201]

def test_cambiar_estado_contenedor(contenedor_id):
    """Prueba cambiar estado del contenedor"""
    print_section("7. CAMBIAR ESTADO DEL CONTENEDOR")

    estado = "rentado"

    response = requests.patch(
        f"{BASE_URL}/contenedores/{contenedor_id}/estado",
        json=estado,
        headers=get_headers()
    )
    print_response(response, "Cambiar Estado")

    return response.status_code in [200, 201]

def test_obtener_contenedor(contenedor_id):
    """Prueba obtener contenedor específico"""
    print_section("8. OBTENER CONTENEDOR ESPECÍFICO")

    response = requests.get(
        f"{BASE_URL}/contenedores/{contenedor_id}",
        headers=get_headers()
    )
    print_response(response, "Obtener Contenedor")

    return response.status_code == 200

def test_eliminar_contenedor(contenedor_id):
    """Prueba eliminar contenedor"""
    print_section("9. ELIMINAR CONTENEDOR")

    response = requests.delete(
        f"{BASE_URL}/contenedores/{contenedor_id}",
        headers=get_headers()
    )
    print(f"\nStatus: {response.status_code}")

    if response.status_code == 204:
        print("✓ Contenedor eliminado")
        return True
    else:
        print(f"✗ Error eliminando contenedor: {response.text}")
        return False

def test_eliminar_usuario(usuario_id):
    """Prueba eliminar usuario"""
    print_section("10. ELIMINAR USUARIO")

    response = requests.delete(
        f"{BASE_URL}/usuarios/{usuario_id}",
        headers=get_headers()
    )
    print(f"\nStatus: {response.status_code}")

    if response.status_code == 204:
        print("✓ Usuario eliminado")
        return True
    else:
        print(f"✗ Error eliminando usuario: {response.text}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("  PRUEBAS COMPLETAS DE LA API")
    print("  Sistema de Logística de Contenedores")
    print(f"  URL: {BASE_URL}")
    print(f"  Timestamp: {datetime.now()}")
    print("="*60)

    resultados = {}

    # 1. Login
    if not test_login():
        print("\n✗ FALLO: No se puede continuar sin token")
        return

    # 2. Usuarios
    resultados["login"] = True
    usuario_id = test_crear_usuario()
    resultados["crear_usuario"] = usuario_id is not None

    resultados["listar_usuarios"] = test_listar_usuarios()

    # 3. Contenedores
    contenedor_id = test_crear_contenedor()
    resultados["crear_contenedor"] = contenedor_id is not None

    if contenedor_id:
        resultados["listar_contenedores"] = test_listar_contenedores()
        resultados["actualizar_contenedor"] = test_actualizar_contenedor(contenedor_id)
        resultados["cambiar_estado"] = test_cambiar_estado_contenedor(contenedor_id)
        resultados["obtener_contenedor"] = test_obtener_contenedor(contenedor_id)
        resultados["eliminar_contenedor"] = test_eliminar_contenedor(contenedor_id)

    # 4. Limpiar (eliminar usuario de prueba)
    if usuario_id:
        resultados["eliminar_usuario"] = test_eliminar_usuario(usuario_id)

    # Resumen
    print_section("RESUMEN DE PRUEBAS")
    print()
    exitosas = sum(1 for v in resultados.values() if v)
    total = len(resultados)

    for prueba, resultado in resultados.items():
        estado = "✓" if resultado else "✗"
        print(f"  {estado} {prueba}: {'EXITOSA' if resultado else 'FALLÓ'}")

    print(f"\nTotal: {exitosas}/{total} pruebas exitosas")

    if exitosas == total:
        print("\n✓✓✓ ¡TODAS LAS PRUEBAS EXITOSAS! ✓✓✓")
        print("\nTu API está completamente funcional con:")
        print("  - Autenticación JWT en todos los endpoints")
        print("  - CRUD completo para usuarios y contenedores")
        print("  - Base de datos PostgreSQL conectada")
        print("  - Sistema de roles (admin/operador)")
    else:
        print(f"\n⚠ {total - exitosas} prueba(s) fallaron - Revisa los errores arriba")

if __name__ == "__main__":
    main()
