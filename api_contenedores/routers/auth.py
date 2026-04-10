from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Usuario
from schemas import Token, LoginRequest
from auth.hashing import verify_password
from auth.jwt import create_access_token

router = APIRouter(prefix='/auth', tags=['Autenticación'])

@router.post('/login', response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica un usuario y devuelve un JWT.
    - **user**: nombre de usuario
    - **password**: contraseña en texto plano
    """
    # Buscar el usuario en la tabla Usuario
    usuario = db.query(Usuario).filter(
        Usuario.user == data.user).first()
    
    if usuario and verify_password(data.password, usuario.password):
        token = create_access_token(user=usuario.user, role=usuario.rol)
        return {
            'access_token': token,
            'token_type': 'bearer',
            'role': usuario.rol
        }

    # Si no coincide ningun usuario
    raise HTTPException(
        status_code=401,
        detail='Usuario o contraseña incorrectos'
    )
