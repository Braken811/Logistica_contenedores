from database import SessionLocal
from models import Usuario
from auth_utils import hash_password
from schemas import RolUsuario

db = SessionLocal()

admin = Usuario(
    nombres="Administrador",
    apellidos="Principal",
    email="admin@contenedores.com",
    user="admin",
    password=hash_password("admin123"),
    rol=RolUsuario.admin
)

db.add(admin)
db.commit()
db.refresh(admin)
print(f" Usuario admin creado con ID: {admin.id_usuario}")
db.close()