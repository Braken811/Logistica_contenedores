from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password: str) -> str:
    """Convierte la contrasena plana a un hash bcrypt seguro."""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Retorna True si la contrasena coincide con el hash almacenado."""
    plain = plain[:72]  # Fix bcrypt 72-byte limit
    return pwd_context.verify(plain, hashed)
