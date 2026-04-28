from passlib.context import CryptContext

# Usar argon2 en lugar de bcrypt (mejor soporte en Python 3.12)
pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')

def hash_password(password: str) -> str:
    """Convierte la contrasena plana a un hash argon2 seguro."""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Retorna True si la contrasena coincide con el hash almacenado."""
    return pwd_context.verify(plain, hashed)
