# Guía Completa de la API - Sistema de Logística de Contenedores

## Estado de la API

✅ **COMPLETAMENTE IMPLEMENTADA**
- JWT Token Authentication en TODOS los endpoints
- CRUD completo para Usuarios y Contenedores
- Base de datos PostgreSQL conectada
- Autenticación por rol (admin, operador)

---

## 1. AUTENTICACIÓN CON JWT

### Endpoint: Login
```
POST /auth/login
```

**Body:**
```json
{
  "user": "admin",
  "password": "tu_contraseña"
}
```

**Respuesta exitosa (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "admin"
}
```

**IMPORTANTE:** Guarda el `access_token`. Lo necesitarás en TODOS los demás endpoints en el header:
```
Authorization: Bearer <access_token>
```

---

## 2. GESTIÓN DE USUARIOS

### 2.1 Listar todos los usuarios
```
GET /usuarios/
Authorization: Bearer <access_token>
```

**Respuesta (200):**
```json
[
  {
    "id_usuario": 1,
    "nombres": "Juan",
    "apellidos": "Pérez",
    "email": "juan@example.com",
    "user": "admin",
    "rol": "admin"
  }
]
```

### 2.2 Obtener usuario específico
```
GET /usuarios/{user_id}
Authorization: Bearer <access_token>
```

### 2.3 Crear nuevo usuario (SOLO ADMIN)
```
POST /usuarios/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body:**
```json
{
  "nombres": "Carlos",
  "apellidos": "García",
  "email": "carlos@example.com",
  "user": "carlos_operador",
  "password": "Password123!",
  "rol": "operador"
}
```

**Respuesta (201):**
```json
{
  "id_usuario": 2,
  "nombres": "Carlos",
  "apellidos": "García",
  "email": "carlos@example.com",
  "user": "carlos_operador",
  "rol": "operador"
}
```

### 2.4 Actualizar usuario (SOLO ADMIN)
```
PUT /usuarios/{user_id}
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body (actualiza solo los campos enviados):**
```json
{
  "email": "carlos.nuevo@example.com",
  "nombres": "Carlos Manuel"
}
```

### 2.5 Eliminar usuario (SOLO ADMIN)
```
DELETE /usuarios/{user_id}
Authorization: Bearer <access_token>
```

**Respuesta (204):** Sin contenido

---

## 3. GESTIÓN DE CONTENEDORES

### 3.1 Listar contenedores (con filtros)
```
GET /contenedores/?codigo=CNT&estado=activo&id_cliente=1&skip=0&limit=100
Authorization: Bearer <access_token>
```

**Parámetros de filtro (todos opcionales):**
- `codigo`: Búsqueda parcial por código
- `estado`: activo, inactivo, en_mantenimiento, disponible, rentado, vendido
- `id_cliente`: ID del cliente
- `id_tipo`: ID del tipo de contenedor
- `skip`: Número de registros a saltar
- `limit`: Límite de registros a retornar (máx 500)

**Respuesta (200):**
```json
[
  {
    "id_contenedor": 1,
    "id_codigo": "CNT001",
    "id_tipo": 1,
    "id_cliente": 1,
    "estado": "activo",
    "ubicacion_actual": "Puerto de Barranquilla",
    "created_at": "2026-04-20",
    "updated_at": "2026-04-28"
  }
]
```

### 3.2 Obtener contenedor específico
```
GET /contenedores/{contenedor_id}
Authorization: Bearer <access_token>
```

### 3.3 Crear contenedor (SOLO ADMIN)
```
POST /contenedores/
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body:**
```json
{
  "id_codigo": "CNT002",
  "id_tipo": 1,
  "id_cliente": 1,
  "estado": "activo",
  "ubicacion_actual": "Puerto de Cartagena"
}
```

**Respuesta (201):** El contenedor creado

### 3.4 Actualizar contenedor (SOLO ADMIN)
```
PUT /contenedores/{contenedor_id}
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body (actualiza solo los campos enviados):**
```json
{
  "ubicacion_actual": "Nuevo puerto",
  "estado": "en_mantenimiento"
}
```

### 3.5 Cambiar estado del contenedor (SOLO ADMIN)
```
PATCH /contenedores/{contenedor_id}/estado
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Body:**
```json
"rentado"
```

**Estados válidos:** activo, inactivo, en_mantenimiento, disponible, rentado, vendido

### 3.6 Eliminar contenedor (SOLO ADMIN)
```
DELETE /contenedores/{contenedor_id}
Authorization: Bearer <access_token>
```

**Respuesta (204):** Sin contenido

### 3.7 Obtener historial completo del contenedor
```
GET /contenedores/{contenedor_id}/historial
Authorization: Bearer <access_token>
```

**Respuesta (200):**
```json
{
  "contenedor": { ... },
  "movimientos": [ ... ],
  "historial_estado": [ ... ],
  "fotos": [ ... ],
  "arrendamientos": [ ... ],
  "facturaciones": [ ... ]
}
```

---

## 4. OTROS ENDPOINTS TAMBIÉN PROTEGIDOS

Todos los siguientes endpoints también **requieren autenticación con JWT**:

### Clientes
- `GET /clientes/` - Listar clientes
- `GET /clientes/{cliente_id}` - Obtener cliente
- `POST /clientes/` - Crear cliente (SOLO ADMIN)
- `PUT /clientes/{cliente_id}` - Actualizar cliente (SOLO ADMIN)
- `DELETE /clientes/{cliente_id}` - Eliminar cliente (SOLO ADMIN)

### Movimientos
- `GET /movimientos/` - Listar movimientos
- `POST /movimientos/` - Crear movimiento (SOLO ADMIN)
- `DELETE /movimientos/{movimiento_id}` - Eliminar movimiento (SOLO ADMIN)

### Historial de Estado
- `GET /historial-estado/` - Listar historial
- `POST /historial-estado/` - Crear registro (SOLO ADMIN)

### Y más...

---

## 5. CÓDIGOS DE RESPUESTA HTTP

- **200 OK**: Solicitud exitosa
- **201 Created**: Recurso creado
- **204 No Content**: Eliminación exitosa
- **400 Bad Request**: Datos inválidos
- **401 Unauthorized**: Token ausente o inválido
- **403 Forbidden**: Sin permisos (no es admin)
- **404 Not Found**: Recurso no encontrado
- **500 Internal Server Error**: Error del servidor

---

## 6. CÓMO PROBAR LA API

### Opción 1: Usar cURL
```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user":"admin","password":"tu_contraseña"}'

# Listar usuarios (con token)
curl -X GET http://localhost:8000/usuarios/ \
  -H "Authorization: Bearer <access_token>"

# Crear contenedor
curl -X POST http://localhost:8000/contenedores/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "id_codigo": "CNT003",
    "id_tipo": 1,
    "id_cliente": 1,
    "estado": "activo",
    "ubicacion_actual": "Bodega Central"
  }'
```

### Opción 2: Usar Postman
1. Colecciona creada automáticamente en `/docs`
2. Haz login en POST `/auth/login`
3. Copia el token
4. En cada request, ve a "Authorization" → "Bearer Token" → Pega el token

### Opción 3: Usar la documentación interactiva
```
http://localhost:8000/docs
```
(Swagger UI con interfaz visual)

---

## 7. INFORMACIÓN DE LA BASE DE DATOS

- **Host:** localhost
- **Puerto:** 5432
- **BD:** contenedores
- **Usuario:** postgres
- **Tablas creadas automáticamente:**
  - usuarios
  - contenedores
  - clientes
  - tipos_contenedores
  - movimientos
  - historial_estado
  - fotos
  - facturacion
  - arrendamiento
  - ventas

---

## 8. CONFIGURACIÓN DE SEGURIDAD

### Secret Key (CAMBIAR EN PRODUCCIÓN)
Archivo: `.env`
```
SECRET_KEY=cambia_esta_clave_secreta_en_produccion_2026
```

### Roles disponibles
- **admin**: Acceso a crear/actualizar/eliminar
- **operador**: Solo lectura

---

## 9. FLUJO TÍPICO DE USO

1. **Login**: POST `/auth/login` → Obtener token
2. **Crear usuario**: POST `/usuarios/` → Crear nuevo operador (ADMIN)
3. **Crear contenedor**: POST `/contenedores/` → Agregar contenedor (ADMIN)
4. **Consultar contenedor**: GET `/contenedores/?codigo=CNT003`
5. **Cambiar estado**: PATCH `/contenedores/{id}/estado` → "rentado"
6. **Ver historial**: GET `/contenedores/{id}/historial`
7. **Eliminar**: DELETE `/contenedores/{id}` (ADMIN)

---

## 10. TROUBLESHOOTING

### "Token inválido o expirado"
- El token tiene validez de 8 horas
- Haz login nuevamente

### "Solo administradores"
- Solo usuarios con rol "admin" pueden crear/actualizar/eliminar
- Pide a un admin que cree tu usuario

### "Conexión a base de datos rechazada"
- Verifica que PostgreSQL está corriendo
- Verifica credenciales en `.env`
- Verifica que la BD "contenedores" existe

---

**API versión 1.0.0 - Talento Tech 2026**
