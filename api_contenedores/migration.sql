-- Ejecutar en PostgreSQL sobre la BD 'contenedores'
-- Aplicar en orden; cada ALTER usa IF NOT EXISTS / IF EXISTS para ser idempotente.

-- 1. Usuario: agregar columnas nuevas
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS email_verificado  BOOLEAN DEFAULT FALSE;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS verification_token VARCHAR;

-- 2. Contenedor: hacer id_cliente nullable si aún es NOT NULL
ALTER TABLE contenedores ALTER COLUMN id_cliente DROP NOT NULL;

-- 3. Contenedor: agregar ruta_imagen
ALTER TABLE contenedores ADD COLUMN IF NOT EXISTS ruta_imagen VARCHAR;

-- 4. Facturacion: agregar columnas nuevas
ALTER TABLE facturacion ADD COLUMN IF NOT EXISTS codigo_factura    VARCHAR;
ALTER TABLE facturacion ADD COLUMN IF NOT EXISTS fecha_vencimiento DATE;
ALTER TABLE facturacion ADD COLUMN IF NOT EXISTS estado_pago       VARCHAR DEFAULT 'pendiente';
ALTER TABLE facturacion ADD COLUMN IF NOT EXISTS id_arrendamiento  INTEGER REFERENCES arrendamiento(id_arrendamiento);

-- 5. Generar códigos automáticos para facturas existentes sin código
UPDATE facturacion
SET    codigo_factura = CONCAT('FAC-', LPAD(id_factura::text, 4, '0'))
WHERE  codigo_factura IS NULL;

-- 6. Usuario: avatar de perfil
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS ruta_imagen VARCHAR;

-- 7. Tabla de notificaciones persistentes (leído/no leído en BD por usuario)
CREATE TABLE IF NOT EXISTS notificaciones (
    id_notificacion SERIAL PRIMARY KEY,
    id_usuario      INTEGER NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    tipo            VARCHAR NOT NULL,
    titulo          VARCHAR NOT NULL,
    mensaje         VARCHAR,
    fecha           TIMESTAMP DEFAULT NOW(),
    leido           BOOLEAN DEFAULT FALSE,
    fecha_lectura   TIMESTAMP,
    ref_id          VARCHAR,
    CONSTRAINT uq_notif_user_ref UNIQUE (id_usuario, ref_id)
);
CREATE INDEX IF NOT EXISTS ix_notificaciones_id_usuario ON notificaciones(id_usuario);
CREATE INDEX IF NOT EXISTS ix_notificaciones_leido      ON notificaciones(id_usuario, leido);

-- 8. Movimientos: fecha de salida explícita (distinta de fecha_hora de registro)
ALTER TABLE movimientos ADD COLUMN IF NOT EXISTS fecha_salida DATE;
