from sqlalchemy import text
from database import engine
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE facturacion ADD COLUMN monto_pagado FLOAT DEFAULT 0.0'))
    conn.commit()
