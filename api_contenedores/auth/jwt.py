from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'cambiar-por-openssl-rand-hex-32-en-produccion')
ALGORITHM = 'HS256'
EXPIRE_MINUTES = int(os.getenv('EXPIRE_MINUTES', 480))  # 8 horas

def create_access_token(user: str, role: str) -> str:
    """Crea un token JWT con el username y el rol del usuario."""
    payload = {
        'sub': user,        # subject: identifica al usuario
        'role': role,       # rol: 'admin' u 'operador'
        'exp': datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict | None:
    """Decodifica el token. Retorna None si es invalido o expirado."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
