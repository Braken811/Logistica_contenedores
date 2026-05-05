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
