# Frontend - API Integration Testing Guide

## Prerequisitos
✅ API running on `http://localhost:8000`
✅ Usuarios creados en la base de datos

## Flujo de Prueba

### 1. **Login Page (`/login`)**
```
URL: http://localhost:8000/login
- Ingresa credenciales válidas de usuario (username + password)
- Espera POST request a /auth/login
- Token JWT debe guardarse en localStorage
- Redirige automáticamente a /dashboard
```

**Verificar en DevTools (F12):**
```javascript
// Storage → Local Storage
localStorage.getItem('mz_auth_token')     // Debe tener un JWT
localStorage.getItem('mz_auth_role')      // admin, supervisor, operador, etc.
localStorage.getItem('mz_auth_user')      // username
```

### 2. **Dashboard Page (`/dashboard`)**
```
URL: http://localhost:8000/dashboard
- Si NO hay token → Redirige a /login
- Si hay token → Carga dashboard
- Token se envía en Authorization header de todas las peticiones
```

**Verificar en DevTools (F12 → Network):**
```
Cualquier petición a /api/... debe tener:
Request Headers:
  Authorization: Bearer eyJhbGc...
  Content-Type: application/json
```

### 3. **Logout**
```
- Click en el card del usuario (avatar + nombre) en sidebar
- Aparece diálogo de confirmación
- Click en "Salir"
- localStorage se limpia
- Redirige a /login
```

## Pruebas Específicas

### Test 1: Login Exitoso
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user":"admin","password":"tu_contraseña"}'

# Response esperado:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "role": "admin"
}
```

### Test 2: Login Fallido
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user":"admin","password":"wrong"}'

# Response esperado (401):
{"detail":"Usuario o contraseña incorrectos"}
```

### Test 3: API Call con Token
```bash
curl -X GET http://localhost:8000/api/contenedores \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json"

# Response esperado (200):
{"ok": true, "data": [...]}
```

### Test 4: API Call sin Token
```bash
curl -X GET http://localhost:8000/api/contenedores

# Response esperado (401):
Error no autorizado
```

## Debugging Console Errors

Si ves errores en la consola, revisa:

1. **CORS Error**: API base URL no es accesible
   - Verifica que API está corriendo en `http://localhost:8000`

2. **Auth Error**: Token no es válido
   - Limpia localStorage: `localStorage.clear()`
   - Vuelve a hacer login

3. **API 401**: Token expirado
   - Limpia localStorage
   - Haz login de nuevo

## Storage Cleanup (si necesitas resetear)
```javascript
// En consola del navegador:
localStorage.clear()
sessionStorage.clear()
// O específicamente:
localStorage.removeItem('mz_auth_token')
localStorage.removeItem('mz_auth_role')
localStorage.removeItem('mz_auth_user')
```

## Documentación API
- `/docs` → Swagger UI
- `/redoc` → ReDoc
