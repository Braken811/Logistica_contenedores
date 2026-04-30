# 🔐 PROTECCIÓN CON JWT + CONEXIÓN A BASE DE DATOS

## ✅ Cambios Realizados

### 1. **Conexión a Base de Datos Mejorada** (`database.py`)
- ✅ Agregado logging para diagnosticar problemas de conexión
- ✅ Verificación de conexión al iniciar la API
- ✅ Connection pooling optimizado (`pool_pre_ping`, `pool_recycle`)
- ✅ Event listeners para conexiones exitosas/fallidas

### 2. **Startup Check** (`main.py`)
- ✅ Verificación de BD en el lifespan de FastAPI
- ✅ Creación de tablas al iniciar
- ✅ Mensajes informativos claros en consola

### 3. **Protección JWT en Todos los Endpoints**

#### Endpoints Protegidos con `only_admin` (POST/PUT/DELETE):
- ✅ `/usuarios` - POST (crear usuario)
- ✅ `/clientes` - POST, PUT, DELETE
- ✅ `/tipos-contenedores` - POST, DELETE
- ✅ `/contenedores` - POST, PUT, PATCH
- ✅ `/movimientos` - DELETE (modificado)
- ✅ `/fotos` - POST, DELETE (modificado)
- ✅ `/historial-estado` - POST (modificado)
- ✅ `/facturacion` - POST, DELETE
- ✅ `/arrendamientos` - POST, PUT
- ✅ `/ventas` - POST, DELETE

#### Endpoints con `get_current_user` (Require cualquier usuario autenticado):
- ✅ GET en todos los recursos
- ✅ POST en movimientos (operadores pueden registrar)

#### Endpoints Públicos:
- ✅ `/auth/login` - Sin protección (login)
- ✅ `/usuarios/public` - Sin protección (crear primer admin)
- ✅ `/` - Info de la API (sin protección)
- ✅ `/login` - Página de login
- ✅ `/dashboard` - Página dashboard

---

## 🔍 Verificar Que Todo Funciona

### Paso 1: Verificar conexión a BD

```bash
cd api_contenedores
python test_database_connection.py
```

**Esperado:**
```
✅ Conexión exitosa a PostgreSQL
✅ Tablas en la base de datos
✅ DIAGNÓSTICO COMPLETADO - TODO CORRECTO
```

**Si falla:**
- Verificar que PostgreSQL está corriendo
- Revisar credenciales en `.env`
- Crear DB: `createdb contenedores`

### Paso 2: Iniciar la API con verificación

```bash
uvicorn main:app --reload
```

**Esperado en logs:**
```
======================================================================
🚀 INICIANDO API - Sistema de Logística de Contenedores
======================================================================
✅ PostgreSQL conectado: PostgreSQL 14...
✅ Tablas de BD inicializadas
```

### Paso 3: Probar API con autenticación

```bash
python test_api_with_auth.py
```

**Esperado:**
```
✅ Usuario admin creado
✅ Login exitoso
✅ Cliente creado
✅ Contenedor creado
✅ Acceso denegado sin token (comportamiento esperado)
```

---

## 📋 Variables en `.env`

Estas están configuradas en `.env`, verifica que sean correctas:

```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=contenedores
DATABASE_USER=postgres
DATABASE_PASSWORD=Mmillan.06

SECRET_KEY=cambia_esta_clave_secreta_en_produccion_2026
EXPIRE_MINUTES=480
```

**⚠️ En producción:**
- Cambiar `SECRET_KEY` a algo más seguro:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- Usar credenciales de BD más fuertes
- Cambiar `EXPIRE_MINUTES` según necesidad

---

## 🔗 Endpoints con Autenticación

### Flujo de autenticación:

1. **Login (sin token):**
   ```bash
   POST /auth/login
   {
     "user": "admin",
     "password": "admin123"
   }
   
   Response:
   {
     "access_token": "eyJhbGciOiJIUzI1NiIs...",
     "token_type": "bearer",
     "role": "admin"
   }
   ```

2. **Usar token en requests:**
   ```bash
   GET /contenedores
   Header: Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
   ```

### Ejemplo con curl:

```bash
# Login
TOKEN=$(curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"user":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# Crear contenedor (requiere admin)
curl -X POST "http://localhost:8000/contenedores" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id_codigo": "CONT-001",
    "id_tipo": 1,
    "id_cliente": 1,
    "estado": "disponible",
    "ubicacion_actual": "Barranquilla"
  }'

# Listar (requiere autenticación)
curl -X GET "http://localhost:8000/contenedores" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🐛 Troubleshooting

### "El token es inválido o expirado"
- Token expiró (por defecto 8 horas)
- Haz login nuevamente con `/auth/login`

### "Solo administradores"
- Endpoint requiere rol `admin`
- Usa usuario con rol admin

### "Base de datos no conecta"
1. Verifica PostgreSQL está corriendo: `sudo service postgresql status`
2. Verifica `.env` tiene credenciales correctas
3. Crea la DB: `createdb contenedores`
4. Reinicia la API

### "Error 422 - Validation Error"
- Verifica que estés enviando JSON válido
- Revisa tipos de datos (integers, strings, dates)
- Ve a `/docs` para esquema de cada endpoint

---

## 📊 Base de Datos

La BD se crea automáticamente con las tablas:
- `usuarios` - Usuarios del sistema
- `clientes` - Clientes
- `tipos_contenedores` - Tipos de contenedores
- `contenedores` - Contenedores logísticos
- `movimientos` - Movimientos de contenedores
- `historial_estado` - Histórico de estados
- `fotos` - Fotos de contenedores
- `arrendamiento` - Arrendamientos
- `facturacion` - Facturas
- `ventas` - Ventas

Para verificar datos guardados:

```bash
python test_database_connection.py
```

---

## 🎯 Próximos Pasos

1. **Frontend**: Actualizar para enviar tokens en headers
   ```javascript
   headers: {
     'Authorization': `Bearer ${token}`,
     'Content-Type': 'application/json'
   }
   ```

2. **Roles**: Sistema de rol ya implementado
   - `admin`: Acceso total
   - `operador`: Acceso limitado

3. **Monitoreo**: Revisar logs de FastAPI en terminal

4. **Documentación**: Ve a `/docs` (Swagger UI) para explorar API interactivamente

---

## ✨ Resumen

| Aspecto | Estado |
|---------|--------|
| JWT Token Protection | ✅ Implementado en todos los endpoints |
| Database Connection | ✅ Mejorado con logging |
| Auto Table Creation | ✅ En startup |
| Admin-only Protection | ✅ POST/PUT/DELETE protegidos |
| Role-based Access | ✅ Admin/Operador |
| Diagnostics | ✅ Scripts de test |
| Documentation | ✅ Auto-generada en /docs |

**Ahora los datos se guardarán correctamente en la BD real y todos los endpoints requieren autenticación JWT.**
