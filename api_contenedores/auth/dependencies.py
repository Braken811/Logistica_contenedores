from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario
from auth.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Extrae y valida el usuario del token JWT."""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token invalido o expirado',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    user_name = payload.get('sub')
    role = payload.get('role')

    user = db.query(Usuario).filter(Usuario.user == user_name).first()
    
    if not user:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')

    return {'user': user, 'role': role}


def only_admin(current=Depends(get_current_user)):
    """Solo permite acceso a administradores."""
    if current['role'] != 'admin':
        raise HTTPException(status_code=403, detail='Solo administradores')
    return current['user']


def only_operador(current=Depends(get_current_user)):
    """Solo permite acceso a operadores."""
    if current['role'] != 'operador':
        raise HTTPException(status_code=403, detail='Solo operadores')
    return current['user']
