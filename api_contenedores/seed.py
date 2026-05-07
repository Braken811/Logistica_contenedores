"""
seed.py — Poblar la BD con datos de ejemplo para Mazolo Contenedores.
Ejecutar desde api_contenedores/:  python seed.py
"""
from datetime import date, datetime, timedelta
from database import SessionLocal
from sqlalchemy import text
from models import (
    Cliente, Contenedor, TipoContenedor, Arrendamiento,
    Movimiento, Facturacion, Notificacion, Usuario, HistorialEstado, Venta
)
from schemas import EstadoContenedor
from auth.hashing import hash_password

def d(days: int) -> date:
    return date.today() + timedelta(days=days)

def dt(days: int) -> datetime:
    return datetime.utcnow() + timedelta(days=days)

db = SessionLocal()

try:
    # ── 0. Limpiar tablas (CASCADE maneja dependencias) ───────────────────────
    print("Limpiando tablas...")
    db.execute(text(
        "TRUNCATE TABLE notificaciones, ventas, fotos, facturacion, "
        "historial_estado, movimientos, arrendamiento, contenedores, "
        "clientes, tipos_contenedores, usuarios RESTART IDENTITY CASCADE"
    ))
    db.commit()
    print("[OK] Tablas limpiadas\n")

    # ── 1. Tipos de contenedores ──────────────────────────────────────────────
    tipos = [
        TipoContenedor(nombre="Dry Container 20'",  descripcion="Contenedor seco estándar de 20 pies"),
        TipoContenedor(nombre="Dry Container 40'",  descripcion="Contenedor seco estándar de 40 pies"),
        TipoContenedor(nombre="Refrigerado 20'",    descripcion="Contenedor refrigerado (reefer) de 20 pies"),
        TipoContenedor(nombre="Open Top 40'",       descripcion="Contenedor techo abierto de 40 pies"),
        TipoContenedor(nombre="Tank Container",     descripcion="Contenedor cisterna para líquidos a granel"),
    ]
    db.add_all(tipos)
    db.flush()
    tipo = {t.nombre: t.id_tipo for t in tipos}
    print(f"[OK] Tipos de contenedor: {len(tipos)} insertados")

    # ── 2. Usuarios ────────────────────────────────────────────────────────────
    usuarios = [
        Usuario(nombres="Administrador", apellidos="Sistema",   email="admin@mazolo.co",        user="admin",    password=hash_password("admin123"),  rol="admin",      email_verificado=True),
        Usuario(nombres="Carlos",        apellidos="Mendoza",   email="cmendoza@mazolo.co",     user="cmendoza", password=hash_password("super123"),  rol="supervisor", email_verificado=True),
        Usuario(nombres="Ana",           apellidos="Torres",    email="atorres@mazolo.co",      user="atorres",  password=hash_password("oper123"),   rol="operador",   email_verificado=True),
        Usuario(nombres="Juan",          apellidos="Ramos",     email="jramos@mazolo.co",       user="jramos",   password=hash_password("oper123"),   rol="operador",   email_verificado=True),
        Usuario(nombres="Sandra",        apellidos="López",     email="slopez@mazolo.co",       user="slopez",   password=hash_password("audit123"),  rol="auditor",    email_verificado=True),
        Usuario(nombres="Miguel",        apellidos="Peña",      email="mpena@mazolo.co",        user="mpena",    password=hash_password("oper123"),   rol="operador",   email_verificado=False),
    ]
    db.add_all(usuarios)
    db.flush()
    u = {usr.user: usr.id_usuario for usr in usuarios}
    print(f"[OK] Usuarios: {len(usuarios)} insertados")

    # ── 3. Clientes ────────────────────────────────────────────────────────────
    clientes = [
        Cliente(nombre="Navieras del Caribe SAS",     nit="500100200", telefono="6054321000", email="navieras@caribe.co",     direccion="Cartagena, Manga"),
        Cliente(nombre="Zona Franca La Candelaria",   nit="500200300", telefono="6055001234", email="info@zonafranca.co",      direccion="Cartagena, Mamonal"),
        Cliente(nombre="Grupo Empresarial Portuario", nit="500300400", telefono="3158009900", email="gep@portuario.co",        direccion="Barranquilla, Puerto Colombia"),
        Cliente(nombre="Inversiones Maritimas Ltda",  nit="500400500", telefono="3004567890", email="inv@maritimas.co",        direccion="Buenaventura, Centro"),
        Cliente(nombre="Trans Andina Cargo SAS",      nit="500500600", telefono="3172345678", email="cargo@transandina.co",    direccion="Bogotá, Fontibón"),
        Cliente(nombre="Exportaciones del Norte SA",  nit="500600700", telefono="3151234567", email="export@delnorte.co",      direccion="Barranquilla, Centro"),
        Cliente(nombre="Importadora Pacífico Ltda",   nit="500700800", telefono="3209876543", email="imp@pacifico.co",         direccion="Cali, Puerto Mallarino"),
        Cliente(nombre="Logística Global SAS",        nit="500800900", telefono="3007654321", email="info@logisticaglobal.co", direccion="Bogotá, Fontibón"),
    ]
    db.add_all(clientes)
    db.flush()
    cli = {c.nombre: c.id_cliente for c in clientes}
    print(f"[OK] Clientes: {len(clientes)} insertados")

    # ── 4. Contenedores ────────────────────────────────────────────────────────
    contenedores = [
        Contenedor(id_codigo="MZLO-001", id_tipo=tipo["Dry Container 20'"], id_cliente=cli["Navieras del Caribe SAS"],     estado=EstadoContenedor.asignado,          ubicacion_actual="Cartagena, Puerto",         created_at=d(-150), updated_at=d(-5)),
        Contenedor(id_codigo="MZLO-002", id_tipo=tipo["Dry Container 40'"], id_cliente=cli["Zona Franca La Candelaria"],   estado=EstadoContenedor.en_transito,       ubicacion_actual="Barranquilla, Puerto",      created_at=d(-140), updated_at=d(-3)),
        Contenedor(id_codigo="MZLO-003", id_tipo=tipo["Refrigerado 20'"],   id_cliente=None,                               estado=EstadoContenedor.disponible,        ubicacion_actual="Cartagena, Patio Norte",    created_at=d(-130), updated_at=d(-10)),
        Contenedor(id_codigo="MZLO-004", id_tipo=tipo["Dry Container 20'"], id_cliente=cli["Grupo Empresarial Portuario"], estado=EstadoContenedor.en_patio,          ubicacion_actual="Bogotá, Fontibón",          created_at=d(-120), updated_at=d(-7)),
        Contenedor(id_codigo="MZLO-005", id_tipo=tipo["Open Top 40'"],      id_cliente=cli["Inversiones Maritimas Ltda"],  estado=EstadoContenedor.en_transito,       ubicacion_actual="Medellín, Guayabal",        created_at=d(-110), updated_at=d(-2)),
        Contenedor(id_codigo="MZLO-006", id_tipo=tipo["Dry Container 40'"], id_cliente=cli["Trans Andina Cargo SAS"],      estado=EstadoContenedor.asignado,          ubicacion_actual="Cali, Puerto Mallarino",    created_at=d(-100), updated_at=d(-1)),
        Contenedor(id_codigo="MZLO-007", id_tipo=tipo["Tank Container"],    id_cliente=None,                               estado=EstadoContenedor.en_mantenimiento,  ubicacion_actual="Buenaventura, Talleres",    created_at=d(-90),  updated_at=d(-15)),
        Contenedor(id_codigo="MZLO-008", id_tipo=tipo["Dry Container 20'"], id_cliente=cli["Exportaciones del Norte SA"],  estado=EstadoContenedor.en_transito,       ubicacion_actual="Bogotá, El Dorado",         created_at=d(-80),  updated_at=d(-4)),
        Contenedor(id_codigo="MZLO-009", id_tipo=tipo["Refrigerado 20'"],   id_cliente=None,                               estado=EstadoContenedor.disponible,        ubicacion_actual="Barranquilla, Zona Franca", created_at=d(-70),  updated_at=d(-20)),
        Contenedor(id_codigo="MZLO-010", id_tipo=tipo["Dry Container 40'"], id_cliente=cli["Logística Global SAS"],        estado=EstadoContenedor.fuera_de_servicio, ubicacion_actual="Cartagena, Patio Sur",      created_at=d(-60),  updated_at=d(-30)),
    ]
    db.add_all(contenedores)
    db.flush()
    cont = {c.id_codigo: c.id_contenedor for c in contenedores}
    print(f"[OK] Contenedores: {len(contenedores)} insertados")

    # ── 5. Historial de estado ─────────────────────────────────────────────────
    historiales = [
        # MZLO-001: disponible → en_patio → en_transito → asignado
        HistorialEstado(id_contenedor=cont["MZLO-001"], estado=EstadoContenedor.disponible,        fecha_inicio=d(-150), fecha_fin=d(-110)),
        HistorialEstado(id_contenedor=cont["MZLO-001"], estado=EstadoContenedor.en_patio,          fecha_inicio=d(-110), fecha_fin=d(-90)),
        HistorialEstado(id_contenedor=cont["MZLO-001"], estado=EstadoContenedor.en_transito,       fecha_inicio=d(-90),  fecha_fin=d(-60)),
        HistorialEstado(id_contenedor=cont["MZLO-001"], estado=EstadoContenedor.asignado,          fecha_inicio=d(-60),  fecha_fin=None),
        # MZLO-002: disponible → asignado → en_transito
        HistorialEstado(id_contenedor=cont["MZLO-002"], estado=EstadoContenedor.disponible,        fecha_inicio=d(-140), fecha_fin=d(-100)),
        HistorialEstado(id_contenedor=cont["MZLO-002"], estado=EstadoContenedor.asignado,          fecha_inicio=d(-100), fecha_fin=d(-50)),
        HistorialEstado(id_contenedor=cont["MZLO-002"], estado=EstadoContenedor.en_transito,       fecha_inicio=d(-50),  fecha_fin=None),
        # MZLO-003: en_mantenimiento → disponible
        HistorialEstado(id_contenedor=cont["MZLO-003"], estado=EstadoContenedor.en_mantenimiento,  fecha_inicio=d(-130), fecha_fin=d(-80)),
        HistorialEstado(id_contenedor=cont["MZLO-003"], estado=EstadoContenedor.disponible,        fecha_inicio=d(-80),  fecha_fin=None),
        # MZLO-004: disponible → en_transito → en_patio
        HistorialEstado(id_contenedor=cont["MZLO-004"], estado=EstadoContenedor.disponible,        fecha_inicio=d(-120), fecha_fin=d(-90)),
        HistorialEstado(id_contenedor=cont["MZLO-004"], estado=EstadoContenedor.en_transito,       fecha_inicio=d(-90),  fecha_fin=d(-50)),
        HistorialEstado(id_contenedor=cont["MZLO-004"], estado=EstadoContenedor.en_patio,          fecha_inicio=d(-50),  fecha_fin=None),
        # MZLO-005: disponible → asignado → en_transito
        HistorialEstado(id_contenedor=cont["MZLO-005"], estado=EstadoContenedor.disponible,        fecha_inicio=d(-110), fecha_fin=d(-70)),
        HistorialEstado(id_contenedor=cont["MZLO-005"], estado=EstadoContenedor.asignado,          fecha_inicio=d(-70),  fecha_fin=d(-30)),
        HistorialEstado(id_contenedor=cont["MZLO-005"], estado=EstadoContenedor.en_transito,       fecha_inicio=d(-30),  fecha_fin=None),
        # MZLO-006: en_patio → asignado
        HistorialEstado(id_contenedor=cont["MZLO-006"], estado=EstadoContenedor.en_patio,          fecha_inicio=d(-100), fecha_fin=d(-40)),
        HistorialEstado(id_contenedor=cont["MZLO-006"], estado=EstadoContenedor.asignado,          fecha_inicio=d(-40),  fecha_fin=None),
        # MZLO-007: disponible → en_patio → en_mantenimiento
        HistorialEstado(id_contenedor=cont["MZLO-007"], estado=EstadoContenedor.disponible,        fecha_inicio=d(-90),  fecha_fin=d(-45)),
        HistorialEstado(id_contenedor=cont["MZLO-007"], estado=EstadoContenedor.en_patio,          fecha_inicio=d(-45),  fecha_fin=d(-20)),
        HistorialEstado(id_contenedor=cont["MZLO-007"], estado=EstadoContenedor.en_mantenimiento,  fecha_inicio=d(-20),  fecha_fin=None),
        # MZLO-008: disponible → asignado → en_transito
        HistorialEstado(id_contenedor=cont["MZLO-008"], estado=EstadoContenedor.disponible,        fecha_inicio=d(-80),  fecha_fin=d(-50)),
        HistorialEstado(id_contenedor=cont["MZLO-008"], estado=EstadoContenedor.asignado,          fecha_inicio=d(-50),  fecha_fin=d(-25)),
        HistorialEstado(id_contenedor=cont["MZLO-008"], estado=EstadoContenedor.en_transito,       fecha_inicio=d(-25),  fecha_fin=None),
        # MZLO-009: en_mantenimiento → disponible
        HistorialEstado(id_contenedor=cont["MZLO-009"], estado=EstadoContenedor.en_mantenimiento,  fecha_inicio=d(-70),  fecha_fin=d(-40)),
        HistorialEstado(id_contenedor=cont["MZLO-009"], estado=EstadoContenedor.disponible,        fecha_inicio=d(-40),  fecha_fin=None),
        # MZLO-010: disponible → en_patio → fuera_de_servicio
        HistorialEstado(id_contenedor=cont["MZLO-010"], estado=EstadoContenedor.disponible,        fecha_inicio=d(-60),  fecha_fin=d(-45)),
        HistorialEstado(id_contenedor=cont["MZLO-010"], estado=EstadoContenedor.en_patio,          fecha_inicio=d(-45),  fecha_fin=d(-30)),
        HistorialEstado(id_contenedor=cont["MZLO-010"], estado=EstadoContenedor.fuera_de_servicio, fecha_inicio=d(-30),  fecha_fin=None),
    ]
    db.add_all(historiales)
    db.flush()
    print(f"[OK] Historial de estado: {len(historiales)} registros insertados")

    # ── 6. Arrendamientos ─────────────────────────────────────────────────────
    arr_data = [
        # Activos — próximos a vencer (generan alertas)
        dict(id_contenedor=cont["MZLO-001"], id_cliente=cli["Navieras del Caribe SAS"],     fecha_inicio=d(-30), fecha_fin=d(2),  valor_alquiler=3_800_000, estado_arrendamiento="activo"),
        dict(id_contenedor=cont["MZLO-002"], id_cliente=cli["Zona Franca La Candelaria"],   fecha_inicio=d(-25), fecha_fin=d(1),  valor_alquiler=2_500_000, estado_arrendamiento="activo"),
        dict(id_contenedor=cont["MZLO-004"], id_cliente=cli["Grupo Empresarial Portuario"], fecha_inicio=d(-20), fecha_fin=d(5),  valor_alquiler=4_200_000, estado_arrendamiento="activo"),
        dict(id_contenedor=cont["MZLO-006"], id_cliente=cli["Inversiones Maritimas Ltda"],  fecha_inicio=d(-15), fecha_fin=d(6),  valor_alquiler=1_900_000, estado_arrendamiento="activo"),
        # Activos con margen amplio
        dict(id_contenedor=cont["MZLO-008"], id_cliente=cli["Trans Andina Cargo SAS"],      fecha_inicio=d(-10), fecha_fin=d(20), valor_alquiler=3_100_000, estado_arrendamiento="activo"),
        dict(id_contenedor=cont["MZLO-005"], id_cliente=cli["Exportaciones del Norte SA"],  fecha_inicio=d(-5),  fecha_fin=d(30), valor_alquiler=2_700_000, estado_arrendamiento="activo"),
        # Finalizados
        dict(id_contenedor=cont["MZLO-001"], id_cliente=cli["Logística Global SAS"],        fecha_inicio=d(-90), fecha_fin=d(-60), valor_alquiler=2_800_000, estado_arrendamiento="finalizado"),
        dict(id_contenedor=cont["MZLO-002"], id_cliente=cli["Importadora Pacífico Ltda"],   fecha_inicio=d(-80), fecha_fin=d(-50), valor_alquiler=3_200_000, estado_arrendamiento="finalizado"),
        dict(id_contenedor=cont["MZLO-004"], id_cliente=cli["Navieras del Caribe SAS"],     fecha_inicio=d(-70), fecha_fin=d(-40), valor_alquiler=1_750_000, estado_arrendamiento="finalizado"),
        dict(id_contenedor=cont["MZLO-003"], id_cliente=cli["Zona Franca La Candelaria"],   fecha_inicio=d(-60), fecha_fin=d(-30), valor_alquiler=2_950_000, estado_arrendamiento="finalizado"),
        dict(id_contenedor=cont["MZLO-006"], id_cliente=cli["Grupo Empresarial Portuario"], fecha_inicio=d(-50), fecha_fin=d(-15), valor_alquiler=4_500_000, estado_arrendamiento="finalizado"),
    ]
    arrs = [Arrendamiento(**a) for a in arr_data]
    db.add_all(arrs)
    db.flush()
    arr_ids = [a.id_arrendamiento for a in arrs]
    print(f"[OK] Arrendamientos: {len(arrs)} insertados")

    # ── 7. Movimientos ────────────────────────────────────────────────────────
    rutas = [
        (cont["MZLO-001"], "Cartagena, Puerto",       "Barranquilla, Puerto Colombia", "Camión",      "Juan Ramos",    u["jramos"]),
        (cont["MZLO-002"], "Barranquilla",             "Bogotá, Fontibón",             "Ferrocarril", "Luis Herrera",  u["atorres"]),
        (cont["MZLO-004"], "Bogotá, Fontibón",         "Medellín, Guayabal",           "Camión",      "Pedro Suárez",  u["mpena"]),
        (cont["MZLO-005"], "Medellín",                 "Cali, Puerto Mallarino",       "Camión",      "Carlos Díaz",   u["jramos"]),
        (cont["MZLO-006"], "Cali",                     "Cartagena, Mamonal",           "Barco",       "Ana Torres",    u["atorres"]),
        (cont["MZLO-008"], "Cartagena, Mamonal",       "Bucaramanga, Zona Industrial", "Camión",      "Miguel Peña",   u["mpena"]),
        (cont["MZLO-001"], "Bucaramanga",              "Bogotá, El Dorado",            "Aéreo",       "Sandra López",  u["admin"]),
        (cont["MZLO-002"], "Bogotá",                   "Barranquilla, Aeropuerto",     "Camión",      "Jorge Castro",  u["cmendoza"]),
        (cont["MZLO-004"], "Barranquilla",             "Cartagena, Bocagrande",        "Camión",      "María Núñez",   u["jramos"]),
        (cont["MZLO-005"], "Cartagena",                "Buenaventura, Muelles",        "Barco",       "Ricardo Mora",  u["atorres"]),
        (cont["MZLO-006"], "Buenaventura",             "Cali, Centro",                 "Camión",      "Gloria Ríos",   u["mpena"]),
        (cont["MZLO-008"], "Medellín, Rionegro",       "Bogotá, Cundinamarca",         "Camión",      "Felipe Ortiz",  u["admin"]),
        (cont["MZLO-009"], "Bogotá, Cundinamarca",     "Cartagena, Puerto",            "Camión",      "Daniela Vega",  u["cmendoza"]),
        (cont["MZLO-003"], "Cartagena, Puerto",        "Santa Marta, SPRC",            "Barco",       "Andrés Parra",  u["jramos"]),
        (cont["MZLO-010"], "Santa Marta",              "Barranquilla, Puerto",         "Camión",      "Claudia Soto",  u["atorres"]),
        (cont["MZLO-001"], "Barranquilla, Puerto",     "Cartagena, Patio Norte",       "Camión",      "Juan Ramos",    u["jramos"]),
        (cont["MZLO-007"], "Cartagena, Patio Norte",   "Buenaventura, Talleres",       "Barco",       "Luis Herrera",  u["mpena"]),
        (cont["MZLO-002"], "Buenaventura, Talleres",   "Cali, Puerto Mallarino",       "Camión",      "Ana Torres",    u["atorres"]),
    ]
    movs = [
        Movimiento(
            id_contenedor=cont_id,
            id_usuario=uid,
            fecha_hora=dt(-(len(rutas) - i) * 3),
            ubicacion_origen=origen,
            ubicacion_destino=destino,
            medio_transporte=medio,
            responsable=resp,
        )
        for i, (cont_id, origen, destino, medio, resp, uid) in enumerate(rutas)
    ]
    db.add_all(movs)
    db.flush()
    print(f"[OK] Movimientos: {len(movs)} insertados")

    # ── 8. Facturación ────────────────────────────────────────────────────────
    facturas = [
        # Finalizados → pagado
        Facturacion(id_contenedor=cont["MZLO-001"], id_arrendamiento=arr_ids[6],  fecha_facturacion=d(-58), monto=2_800_000, codigo_factura="FAC-2026-001", fecha_vencimiento=d(-55), estado_pago="pagado",    observaciones="Arrendamiento mensual"),
        Facturacion(id_contenedor=cont["MZLO-002"], id_arrendamiento=arr_ids[7],  fecha_facturacion=d(-48), monto=3_200_000, codigo_factura="FAC-2026-002", fecha_vencimiento=d(-45), estado_pago="pagado",    observaciones="Arrendamiento mensual"),
        Facturacion(id_contenedor=cont["MZLO-004"], id_arrendamiento=arr_ids[8],  fecha_facturacion=d(-38), monto=1_750_000, codigo_factura="FAC-2026-003", fecha_vencimiento=d(-35), estado_pago="pagado",    observaciones="Primer pago"),
        Facturacion(id_contenedor=cont["MZLO-003"], id_arrendamiento=arr_ids[9],  fecha_facturacion=d(-28), monto=2_950_000, codigo_factura="FAC-2026-004", fecha_vencimiento=d(-25), estado_pago="pagado",    observaciones="Arrendamiento completo"),
        Facturacion(id_contenedor=cont["MZLO-006"], id_arrendamiento=arr_ids[10], fecha_facturacion=d(-13), monto=4_500_000, codigo_factura="FAC-2026-005", fecha_vencimiento=d(-10), estado_pago="pagado",    observaciones="Liquidación final"),
        # Activos → mora / pendiente
        Facturacion(id_contenedor=cont["MZLO-001"], id_arrendamiento=arr_ids[0],  fecha_facturacion=d(-15), monto=3_800_000, codigo_factura="FAC-2026-006", fecha_vencimiento=d(-3),  estado_pago="mora",      observaciones="Próximo a vencer — gestionar cobro"),
        Facturacion(id_contenedor=cont["MZLO-002"], id_arrendamiento=arr_ids[1],  fecha_facturacion=d(-12), monto=2_500_000, codigo_factura="FAC-2026-007", fecha_vencimiento=d(2),   estado_pago="pendiente", observaciones="Pendiente confirmación"),
        Facturacion(id_contenedor=cont["MZLO-004"], id_arrendamiento=arr_ids[2],  fecha_facturacion=d(-8),  monto=4_200_000, codigo_factura="FAC-2026-008", fecha_vencimiento=d(7),   estado_pago="pendiente", observaciones="En proceso"),
        Facturacion(id_contenedor=cont["MZLO-006"], id_arrendamiento=arr_ids[3],  fecha_facturacion=d(-5),  monto=1_900_000, codigo_factura="FAC-2026-009", fecha_vencimiento=d(10),  estado_pago="pendiente", observaciones="Primer pago del contrato"),
        Facturacion(id_contenedor=cont["MZLO-008"], id_arrendamiento=arr_ids[4],  fecha_facturacion=d(-2),  monto=3_100_000, codigo_factura="FAC-2026-010", fecha_vencimiento=d(15),  estado_pago="pendiente", observaciones="Cuota inicial"),
        # Servicios adicionales sin arrendamiento
        Facturacion(id_contenedor=cont["MZLO-003"], id_arrendamiento=None, fecha_facturacion=d(-20), monto=850_000,  codigo_factura="FAC-2026-011", fecha_vencimiento=d(-10), estado_pago="pagado",    observaciones="Servicio de inspección"),
        Facturacion(id_contenedor=cont["MZLO-007"], id_arrendamiento=None, fecha_facturacion=d(-7),  monto=420_000,  codigo_factura="FAC-2026-012", fecha_vencimiento=d(5),   estado_pago="pendiente", observaciones="Mantenimiento preventivo"),
    ]
    db.add_all(facturas)
    db.flush()
    print(f"[OK] Facturación: {len(facturas)} facturas insertadas")

    # ── 9. Ventas ─────────────────────────────────────────────────────────────
    ventas = [
        Venta(id_contenedor=cont["MZLO-010"], id_cliente=cli["Importadora Pacífico Ltda"],  fecha_venta=d(-60), precio=45_000_000),
        Venta(id_contenedor=cont["MZLO-009"], id_cliente=cli["Exportaciones del Norte SA"], fecha_venta=d(-30), precio=38_500_000),
    ]
    db.add_all(ventas)
    db.flush()
    print(f"[OK] Ventas: {len(ventas)} insertadas")

    # ── 10. Notificaciones ────────────────────────────────────────────────────
    todos_ids = [u["admin"], u["cmendoza"], u["atorres"], u["jramos"], u["slopez"]]
    notif_base = [
        dict(tipo="error", titulo="Arrendamiento crítico — MZLO-001",    mensaje="Cliente: Navieras del Caribe SAS · Vence en 2 días",        ref_id="arr_err_001"),
        dict(tipo="error", titulo="Arrendamiento crítico — MZLO-002",    mensaje="Cliente: Zona Franca La Candelaria · Vence en 1 día",        ref_id="arr_err_002"),
        dict(tipo="warn",  titulo="Arrendamiento por vencer — MZLO-004", mensaje="Cliente: Grupo Empresarial Portuario · Vence en 5 días",     ref_id="arr_wrn_004"),
        dict(tipo="warn",  titulo="Arrendamiento por vencer — MZLO-006", mensaje="Cliente: Inversiones Maritimas Ltda · Vence en 6 días",      ref_id="arr_wrn_006"),
        dict(tipo="info",  titulo="Movimiento — MZLO-001",               mensaje="Cartagena, Puerto → Barranquilla, Puerto Colombia",          ref_id="mov_inf_001"),
        dict(tipo="info",  titulo="Movimiento — MZLO-002",               mensaje="Barranquilla → Bogotá, Fontibón",                           ref_id="mov_inf_002"),
        dict(tipo="info",  titulo="Movimiento — MZLO-005",               mensaje="Medellín → Cali, Puerto Mallarino",                         ref_id="mov_inf_005"),
        dict(tipo="warn",  titulo="Factura en mora — FAC-2026-006",      mensaje="Contenedor MZLO-001 · $3.800.000 · Vencida hace 3 días",    ref_id="fact_mora_006"),
    ]
    notifs = []
    for uid_val in todos_ids:
        for n in notif_base:
            notifs.append(Notificacion(
                id_usuario=uid_val,
                tipo=n["tipo"],
                titulo=n["titulo"],
                mensaje=n["mensaje"],
                ref_id=f"u{uid_val}_{n['ref_id']}",
                leido=False,
                fecha=datetime.utcnow() - timedelta(hours=len(notifs) % 48),
            ))
    db.add_all(notifs)
    db.flush()
    print(f"[OK] Notificaciones: {len(notifs)} insertadas ({len(notif_base)} tipos × {len(todos_ids)} usuarios)")

    db.commit()
    print("\n[DONE] Seed completado exitosamente.")
    print("\nCredenciales de acceso:")
    print("  admin    / admin123   → Administrador")
    print("  cmendoza / super123   → Supervisor")
    print("  atorres  / oper123    → Operador")
    print("  jramos   / oper123    → Operador")
    print("  slopez   / audit123   → Auditor")

except Exception as e:
    db.rollback()
    print(f"\n[ERROR] {e}")
    raise
finally:
    db.close()
