# API — Sistema de Logística y Monitoreo de Contenedores
**Proyecto Talento Tech 2026** | FastAPI + SQL Server

---

## Estructura del proyecto

```
api_contenedores/
├── main.py               # Punto de entrada, registro de routers
├── database.py           # Conexión SQLAlchemy a SQL Server
├── models.py             # Modelos ORM (9 tablas)
├── schemas.py            # Schemas Pydantic (validación entrada/salida)
├── auth_utils.py         # JWT + hashing de contraseñas (bcrypt)
├── requirements.txt
├── .env.example
└── routers/
    ├── auth.py               # POST /auth/login
    ├── usuarios.py           # CRUD /usuarios
    ├── clientes.py           # CRUD /clientes
    ├── tipos_contenedores.py # CRUD /tipos-contenedores
    ├── contenedores.py       # CRUD + filtros + estado + historial
    ├── movimientos.py        # CRUD /movimientos
    ├── historial_estado.py   # /historial-estado
    ├── fotos.py              # Upload /fotos
    ├── facturacion.py        # CRUD /facturacion
    ├── arrendamiento.py      # CRUD + alertas vencimiento
    ├── ventas.py             # CRUD /ventas
    └── dashboard.py          # GET /dashboard/stats
```

---

## Instalación

### 1. Requisitos previos
- Python 3.10+
- SQL Server con ODBC Driver 17
- El script `Gestion_Contenedores.sql` ejecutado en la BD

### 2. Clonar e instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
```bash
cp .env.example .env
```

### 4. Ejecutar el servidor
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Documentación interactiva
Abre en el navegador:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:**       http://localhost:8000/redoc

---

## Endpoints por módulo

### 🔐 Autenticación
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/login` | Iniciar sesión → devuelve JWT |

### 👤 Usuarios *(solo admin)*
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/usuarios/` | Listar usuarios |
| GET | `/usuarios/{id}` | Obtener usuario |
| POST | `/usuarios/` | Crear usuario |
| PUT | `/usuarios/{id}` | Actualizar usuario |
| DELETE | `/usuarios/{id}` | Eliminar usuario |

### 🏢 Clientes
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/clientes/` | Listar clientes |
| GET | `/clientes/{id}` | Obtener cliente |
| POST | `/clientes/` | Crear cliente |
| PUT | `/clientes/{id}` | Actualizar cliente |
| DELETE | `/clientes/{id}` | Eliminar cliente |

### 📦 Contenedores *(RF01 – RF06, RF10)*
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/contenedores/` | Listar con filtros (codigo, estado, cliente, tipo) |
| GET | `/contenedores/{id}` | Obtener contenedor |
| POST | `/contenedores/` | Crear contenedor |
| PUT | `/contenedores/{id}` | Actualizar contenedor |
| PATCH | `/contenedores/{id}/estado` | Actualizar estado operativo |
| DELETE | `/contenedores/{id}` | Eliminar contenedor |
| GET | `/contenedores/{id}/historial` | Historial completo (RF10) |

### 🚚 Movimientos *(RF01)*
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/movimientos/` | Listar movimientos |
| GET | `/movimientos/contenedor/{id}` | Movimientos de un contenedor |
| POST | `/movimientos/` | Registrar movimiento |
| DELETE | `/movimientos/{id}` | Eliminar movimiento |

### 📊 Dashboard *(RF07)*
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/dashboard/stats` | KPIs: totales, distribuciones, alertas |

### 📋 Arrendamientos *(RF09)*
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/arrendamientos/` | Listar arrendamientos |
| GET | `/arrendamientos/proximos-vencer?dias=7` | Alertas de vencimiento |
| POST | `/arrendamientos/` | Registrar arrendamiento |
| PUT | `/arrendamientos/{id}` | Actualizar arrendamiento |
| DELETE | `/arrendamientos/{id}` | Eliminar arrendamiento |

### 🖼️ Fotos, Facturación, Ventas, Historial de Estado
Rutas CRUD estándar bajo `/fotos`, `/facturacion`, `/ventas`, `/historial-estado`.

---

## Seguridad

- Contraseñas almacenadas con **bcrypt** (`VARBINARY` en SQL Server)
- Autenticación mediante **JWT Bearer Token** (8h de expiración)
- Rutas protegidas por rol: `admin` u `operador`
- Rutas de escritura/eliminación restringidas a `admin`

---

## Flujo de uso recomendado

```
1. POST /auth/login           → obtener token
2. GET  /tipos-contenedores/  → verificar catálogo
3. POST /clientes/            → registrar cliente
4. POST /contenedores/        → crear contenedor
5. PATCH /contenedores/{id}/estado → cambiar estado
6. POST /movimientos/         → registrar movimiento
7. GET  /dashboard/stats      → ver KPIs
```
