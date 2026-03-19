# API de Logística y Monitoreo de Contenedores

## Configuración de PostgreSQL

### 1. Instalar PostgreSQL y pg admin
Descarga e instala PostgreSQL desde https://www.postgresql.org/download/

### 2. Crear la base de datos
```sql
CREATE DATABASE contenedores;
```

### 3. Configurar credenciales
Edita el archivo `.env` con tus credenciales de PostgreSQL:

```env
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=contenedores
DATABASE_USER=tu_usuario
DATABASE_PASSWORD=tu_password
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Crear tablas
Ejecuta el script de inicialización:
```bash
python init_db.py
```

### 6. Ejecutar la aplicación
```bash
uvicorn main:app --reload
```

La API estará disponible en http://127.0.0.1:8000

## Campos de configuración requeridos
- `DATABASE_HOST`: Dirección del servidor PostgreSQL (ej: localhost, 127.0.0.1, IP remota)
- `DATABASE_PORT`: Puerto del servidor (por defecto: 5432)
- `DATABASE_NAME`: Nombre de la base de datos (ej: contenedores)
- `DATABASE_USER`: Usuario de PostgreSQL
- `DATABASE_PASSWORD`: Contraseña del usuario

## Estructura de la base de datos
Las tablas se crean automáticamente con SQLAlchemy:
- usuarios
- clientes
- tipos_contenedores
- contenedores
- movimientos
- historial_estado
- fotos
- facturacion
- arrendamiento
- ventas